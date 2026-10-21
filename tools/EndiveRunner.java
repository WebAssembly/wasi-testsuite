///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 11+
//DEPS info.picocli:picocli:4.7.7
//DEPS io.roastedroot:zerofs:0.1.0
//DEPS run.endive:runtime:1.1.0
//DEPS run.endive:wasi:1.1.0

// `jbang export fatjar` rejects a main class in the unnamed package.
package endive;

import io.roastedroot.zerofs.Configuration;
import io.roastedroot.zerofs.ZeroFs;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.FileSystem;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.Callable;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;
import run.endive.runtime.ImportValues;
import run.endive.runtime.Instance;
import run.endive.wasi.WasiExitException;
import run.endive.wasi.WasiOptions;
import run.endive.wasi.WasiPreview1;
import run.endive.wasm.Parser;

@Command(
        name = "endive",
        mixinStandardHelpOptions = true,
        versionProvider = EndiveRunner.Version.class,
        description =
                "Run a WASI preview 1 command module with endive, on an in-memory ZeroFs"
                        + " filesystem.")
public class EndiveRunner implements Callable<Integer> {

    @Option(
            names = "--env",
            paramLabel = "NAME=VALUE",
            description = "Set an environment variable for the module.")
    Map<String, String> env = new LinkedHashMap<>();

    @Option(
            names = "--dir",
            paramLabel = "HOST[::GUEST]",
            description =
                    "Copy a host directory into the in-memory filesystem and preopen it, at"
                            + " GUEST if given.")
    List<String> dirs = new ArrayList<>();

    @Parameters(index = "0", paramLabel = "FILE.wasm", description = "The module to run.")
    Path wasm;

    @Parameters(index = "1..*", paramLabel = "ARGS", description = "Arguments for the module.")
    List<String> args = new ArrayList<>();

    public static void main(String[] args) {
        int exitCode =
                new CommandLine(new EndiveRunner())
                        .setStopAtPositional(true)
                        .setExpandAtFiles(false)
                        .execute(args);
        System.exit(exitCode);
    }

    @Override
    public Integer call() throws IOException {
        try (FileSystem fs =
                ZeroFs.newFileSystem(
                        Configuration.unix().toBuilder().setAttributeViews("unix").build())) {
            return run(fs);
        }
    }

    private int run(FileSystem fs) throws IOException {
        var options = WasiOptions.builder().inheritSystemStreams();
        env.forEach(options::withEnvironment);
        for (var dir : dirs) {
            var parts = dir.split("::", 2);
            var host = Path.of(parts[0]);
            var guest = parts.length > 1 ? parts[1] : parts[0];
            options.withDirectory(guest, copyToZeroFs(fs, host, guest));
        }

        List<String> argv = new ArrayList<>();
        argv.add(wasm.getFileName().toString());
        argv.addAll(args);
        options.withArguments(argv);

        int exitCode = 0;
        try (var wasi = WasiPreview1.builder().withOptions(options.build()).build()) {
            Instance.builder(Parser.parse(wasm))
                    .withImportValues(
                            ImportValues.builder().addFunction(wasi.toHostFunctions()).build())
                    .build();
        } catch (WasiExitException e) {
            exitCode = e.exitCode();
        }
        System.out.flush();
        System.err.flush();
        return exitCode;
    }

    private static Path copyToZeroFs(FileSystem fs, Path host, String guest) throws IOException {
        var target = fs.getPath(guest).toAbsolutePath();
        if (target.getParent() != null) {
            Files.createDirectories(target.getParent());
        }
        run.endive.wasi.Files.copyDirectory(host, target);
        return target;
    }

    public static class Version implements CommandLine.IVersionProvider {
        @Override
        public String[] getVersion() throws IOException {
            var props = new Properties();
            try (InputStream in =
                    Instance.class.getResourceAsStream(
                            "/META-INF/maven/run.endive/runtime/pom.properties")) {
                if (in != null) {
                    props.load(in);
                }
            }
            return new String[] {"endive " + props.getProperty("version", "unknown")};
        }
    }
}
