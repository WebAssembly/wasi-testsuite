import * as childProcess from "child_process";
import * as fs from "fs";
import * as path from "path";

export async function execAsPromise(command: string): Promise<void> {
    return new Promise<void>((resolve, reject) => {
        childProcess.exec(command, (error) => {
            error ? reject(error) : resolve();
        });
    });
}

export function getPathsInDirectory(directory: string): string[] {
    return fs.readdirSync(directory).map(filepath => path.join(directory, filepath));
}

export function doesFileHaveExtension(filepath: string, extension: string): boolean {
    return !!filepath.match(`^.*\\.${extension}$`);
}

export function mapFileExtension(filepath: string, oldExtension: string, newExtension: string): string {
    return path.join(path.dirname(filepath), path.basename(filepath, oldExtension) + newExtension);
}
