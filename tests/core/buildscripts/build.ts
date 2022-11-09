import { doesFileHaveExtension, execAsPromise, getPathsInDirectory, mapFileExtension } from "./utility";

async function compileWithAsc(inputFilePath: string, outputFilePath: string) {
    return execAsPromise(`npm run asc --silent -- "${inputFilePath}" -o "${outputFilePath}"`);
}

async function compileTests() {
    const testSuiteFiles = getPathsInDirectory("testsuite");
    const testFiles = testSuiteFiles.filter(filepath => doesFileHaveExtension(filepath, "ts"));
    const pendingCompilations = testFiles.map(filepath => compileWithAsc(filepath,  mapFileExtension(filepath, "ts", "wasm")));
    return Promise.all(pendingCompilations);
}

compileTests()
    .then(() => console.log("Tests compiled"))
    .catch((e) => console.error(`Tests failed to compile: ${e}`));
