import * as process from "process";
import { doesFileHaveExtension, execAsPromise, getFileModifiedTimestamp, getPathsInDirectory, mapFileExtension } from "./utility";

async function compileWithAsc(inputFilePath: string, outputFilePath: string) {
    console.log(`Compiling ${inputFilePath}`);
    return execAsPromise(`npm run asc --silent -- "${inputFilePath}" -o "${outputFilePath}"`);
}

function isBinaryOutdated(srcPath: string, wasmPath: string): boolean {
    const sourceTs = getFileModifiedTimestamp(srcPath);
    if (!sourceTs) {
        throw new Error(`Source file ${srcPath} doesn't exist`);
    }
    const wasmTs = getFileModifiedTimestamp(wasmPath);

    return !wasmTs || sourceTs > wasmTs;
}

async function compileTests() {
    const testSuiteFiles = getPathsInDirectory("testsuite");
    const pendingCompilations = testSuiteFiles
        .filter(filePath => doesFileHaveExtension(filePath, "ts"))
        .map(filePath => ({ src: filePath, wasm: mapFileExtension(filePath, "ts", "wasm") }))
        .filter(files => isBinaryOutdated(files.src, files.wasm))
        .map(files => compileWithAsc(files.src, files.wasm)
            .then(_ => undefined)
            .catch(error => ({ source: files.src, error })));

    const errors = (await Promise.allSettled(pendingCompilations))
        .map(p => {
            if (p.status === 'fulfilled' && p.value !== undefined) {
                return `Failed to compile ${p.value.source}:\n${p.value.error}`;
            } else if (p.status === 'rejected') {
                return `Execution failed:\n${p.reason}`;
            } else {
                return undefined;
            }
        }).filter(p => p !== undefined) as string[];

    if (errors.length > 0) {
        throw new Error(errors.join('\n\n'));
    }
}

compileTests()
    .then(() => console.log("Tests compiled"))
    .catch((e) => {
        console.error(`Tests failed to compile:`);
        console.error(e);
        process.exit(1);
    });
