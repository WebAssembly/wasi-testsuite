import { spawnSync } from "node:child_process";
import { mkdir, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { Readable } from "node:stream";
import { pathToFileURL } from "node:url";

const WASI_CLI_RUN_EXPORT = "wasi:cli/run@0.3.0";

function parseArgs(argv) {
  const options = {};
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--version") {
      options.version = true;
    } else if (arg.startsWith("--")) {
      options[arg.slice(2)] = argv[++i];
    } else {
      throw new Error(`unexpected argument: ${arg}`);
    }
  }
  return options;
}

function requireOption(options, name) {
  if (!options[name]) {
    throw new Error(`missing required option --${name}`);
  }
  return options[name];
}

async function ensurePackageLink(outputDir, packageName, packagePath) {
  const scopeDir = join(outputDir, "node_modules", "@bytecodealliance");
  await mkdir(scopeDir, { recursive: true });
  const linkPath = join(scopeDir, packageName);

  try {
    await symlink(
      resolve(packagePath),
      linkPath,
      process.platform === "win32" ? "junction" : "dir",
    );
  } catch (err) {
    if (err?.code !== "EEXIST") {
      throw err;
    }
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const jco = requireOption(options, "jco");

  if (options.version) {
    const result = spawnSync(process.execPath, [jco, "--version"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "inherit"],
    });
    process.stdout.write(result.stdout);
    process.exit(result.status ?? 1);
  }

  const jcoWorkspace = resolve(requireOption(options, "jco-workspace"));
  const component = resolve(requireOption(options, "component"));
  const testName = requireOption(options, "test-name");
  const args = JSON.parse(requireOption(options, "args"));
  const env = JSON.parse(requireOption(options, "env"));
  const preopens = JSON.parse(requireOption(options, "preopens"));

  const outputRoot = await fsMkdtemp("wasi-jco-");
  let completed = false;
  try {
    const moduleName = basename(component, ".wasm");
    const outputDir = join(outputRoot, moduleName);
    await mkdir(outputDir, { recursive: true });

    const { transpile } = await import(
      pathToFileURL(join(jcoWorkspace, "node_modules", "@bytecodealliance", "jco", "src", "api.js"))
    );
    const { files } = await transpile(await readFile(component), {
      name: moduleName,
      minify: process.env.DEBUG ? false : true,
      validLiftingOptimization: true,
      tlaCompat: true,
      optimize: false,
      base64Cutoff: 0,
      instantiation: "async",
      asyncMode: "jspi",
      asyncExports: ["wasi:cli/run#run"],
      wasiShim: true,
      strict: true,
      noTypescript: true,
      outDir: outputDir,
    });

    await Promise.all(
      Object.entries(files).map(async ([path, contents]) => {
        await mkdir(dirname(path), { recursive: true });
        await writeFile(path, contents);
      }),
    );

    await writeFile(join(outputDir, "package.json"), JSON.stringify({ type: "module" }));
    await ensurePackageLink(
      outputDir,
      "preview2-shim",
      join(jcoWorkspace, "node_modules", "@bytecodealliance", "preview2-shim"),
    );
    await ensurePackageLink(
      outputDir,
      "preview3-shim",
      join(jcoWorkspace, "node_modules", "@bytecodealliance", "preview3-shim"),
    );

    const shimSetup = join(outputDir, "__wasi_shim_setup.mjs");
    await writeFile(
      shimSetup,
      `
            export * as cli from "@bytecodealliance/preview3-shim/cli";
            export * as p2cli from "@bytecodealliance/preview2-shim/cli";
            export * as p2io from "@bytecodealliance/preview2-shim/io";
            export * as p3clocks from "@bytecodealliance/preview3-shim/clocks";
            export * as p2fs from "@bytecodealliance/preview2-shim/filesystem";
            export * as p3fs from "@bytecodealliance/preview3-shim/filesystem";
            export * as p3http from "@bytecodealliance/preview3-shim/http";
            export * as p3random from "@bytecodealliance/preview3-shim/random";
            export * as p3sockets from "@bytecodealliance/preview3-shim/sockets";
            export * as streamShim from "@bytecodealliance/preview3-shim/stream";
            export * as futureShim from "@bytecodealliance/preview3-shim/future";
        `,
    );
    const {
      cli,
      p2cli,
      p2io,
      p2fs,
      p3clocks,
      p3fs,
      p3http,
      p3random,
      p3sockets,
      streamShim,
      futureShim,
    } = await import(pathToFileURL(shimSetup));

    cli._setArgs([testName, ...args]);
    cli._setEnv(env);
    cli._setCwd(null);
    cli._setTerminalStdin(null);
    cli._setTerminalStdout(null);
    cli._setTerminalStderr(null);
    p2cli._setArgs([testName, ...args]);
    p2cli._setEnv(env);
    p2cli._setCwd(null);
    p2cli._setTerminalStdin(null);
    p2cli._setTerminalStdout(null);
    p2cli._setTerminalStderr(null);

    cli.stdin.readViaStream = () => {
      const readable = Readable.toWeb(process.stdin);
      const { tx, rx } = futureShim.future();
      tx.write({ tag: "ok", val: undefined }).catch(() => {});
      return [new streamShim.StreamReader(readable), rx];
    };

    const preopenMap = Object.fromEntries(preopens.map(({ guest, host }) => [guest, host]));
    p2fs._setPreopens(preopenMap);
    p3fs._setPreopens(preopenMap);

    const imports = {
      "wasi:cli/environment": cli.environment,
      "wasi:cli/exit": cli.exit,
      "wasi:cli/stderr": { ...p2cli.stderr, ...cli.stderr },
      "wasi:cli/stdin": { ...p2cli.stdin, ...cli.stdin },
      "wasi:cli/stdout": { ...p2cli.stdout, ...cli.stdout },
      "wasi:cli/terminal-input": p2cli.terminalInput,
      "wasi:cli/terminal-output": p2cli.terminalOutput,
      "wasi:cli/terminal-stderr": p2cli.terminalStderr,
      "wasi:cli/terminal-stdin": p2cli.terminalStdin,
      "wasi:cli/terminal-stdout": p2cli.terminalStdout,
      "wasi:clocks/monotonic-clock": p3clocks.monotonicClock,
      "wasi:clocks/system-clock": p3clocks.systemClock,
      "wasi:filesystem/preopens": p3fs.preopens,
      "wasi:filesystem/types": p3fs.types,
      "wasi:http/outgoing-handler": p3http.client,
      "wasi:http/types": p3http.types,
      "wasi:io/error": p2io.error,
      "wasi:io/poll": p2io.poll,
      "wasi:io/streams": p2io.streams,
      "wasi:random/insecure": p3random.insecure,
      "wasi:random/insecure-seed": p3random.insecureSeed,
      "wasi:random/random": p3random.random,
      "wasi:sockets/ip-name-lookup": p3sockets.ipNameLookup,
      "wasi:sockets/types": p3sockets.types,
    };

    // Enable JCO debug printing
    if (process.env.DEBUG) {
      process.env.JCO_DEBUG = "true";
    }

    const module = await import(pathToFileURL(join(outputDir, `${moduleName}.js`)));
    const instance =
      typeof module.instantiate === "function"
        ? await module.instantiate(undefined, imports)
        : module;

    if (instance.$init) {
      await instance.$init;
    }

    const runInterface = instance[WASI_CLI_RUN_EXPORT] ?? instance.run;
    if (
      typeof runInterface !== "object" ||
      runInterface === null ||
      typeof runInterface.run !== "function"
    ) {
      throw new Error(`${WASI_CLI_RUN_EXPORT}.run export missing`);
    }

    const result = await runInterface.run();
    if (result !== undefined) {
      throw new Error(`unexpected run result: ${JSON.stringify(result)}`);
    }
    completed = true;
  } finally {
    if (!process.env.DEBUG) {
      await rm(outputRoot, { recursive: true, force: true });
    }
  }

  if (completed) {
    process.exit(0);
  }
}

async function fsMkdtemp(prefix) {
  const { mkdtemp } = await import("node:fs/promises");
  return mkdtemp(join(tmpdir(), prefix));
}

async function readFile(path) {
  const { readFile } = await import("node:fs/promises");
  return readFile(path);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
