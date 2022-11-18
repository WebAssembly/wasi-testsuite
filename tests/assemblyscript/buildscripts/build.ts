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
        .map(filePath => ({ src: filePath, wasm: mapFileExtension(filePath, "ts", "wasm")}))
        .filter(files => isBinaryOutdated(files.src, files.wasm))
        .map(files => compileWithAsc(files.src, files.wasm));
    return Promise.allSettled(pendingCompilations);
}

compileTests()
    .then(() => console.log("Tests compiled"))
    .catch((e) => {
        console.error(`Tests failed to compile: ${e}`);
        process.exit(1);
    });
