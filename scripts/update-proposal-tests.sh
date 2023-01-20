#!/bin/bash
set -ueo pipefail

REPOS=(
    "wasi-threads"
)

WASI_VERSION=16
WASI_SDK_DIR=$(pwd)/wasi-sdk
BASE_BRANCH="prod/testsuite-base"
PROPOSALS_DIR="tests/proposals"

ENABLED_REPOS=$REPOS
if [[ $# -gt 0 ]] ; then
    ENABLED_REPOS=$@
fi


function install_wasi_sdk()
{
    curl -L -f https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${WASI_VERSION}/wasi-sdk-${WASI_VERSION}.0-linux.tar.gz --output wasi-sdk.tar.gz
    tar xvf wasi-sdk.tar.gz
    mv wasi-sdk-${WASI_VERSION}.0 $WASI_SDK_DIR
}

function build_wasi-threads()
{
    # Compile wasi-libc with thread support as it's not available yet in wasi-sdk
    git clone https://github.com/WebAssembly/wasi-libc.git
    pushd wasi-libc
    CC=$WASI_SDK_DIR/bin/clang make -j 15 THREAD_MODEL=posix
    SYSROOT=$(pwd)/sysroot
    popd
    CC="$WASI_SDK_DIR/bin/clang -D_REENTRANT -matomics -Wl,--import-memory -Wl,--shared-memory --sysroot=$SYSROOT --target=wasm32-wasi-threads -Wno-error=implicit-function-declaration" ./build.sh
}

function update_repo()
{
    repo=$1
    temp_dir=$(mktemp -d)

    echo "Updating tests for the $repo proposal..."

    rm -rf $PROPOSALS_DIR/$repo
    pushd $temp_dir
    git clone https://github.com/WebAssembly/$repo
    popd

    pushd $temp_dir/$repo/test
    build_$repo
    popd

    cp -r $temp_dir/$repo/test/testsuite $PROPOSALS_DIR/$repo
    echo "Updating tests for the $repo proposal completed"

    rm -rf $temp_dir
}

install_wasi_sdk

mkdir -p $PROPOSALS_DIR

git fetch origin $BASE_BRANCH:$BASE_BRANCH
git merge $BASE_BRANCH

for repo in ${REPOS[@]}; do
    if [[ ! " ${ENABLED_REPOS[*]} " =~ " ${repo} " ]]; then
        echo "$repo is not enabled for update"
        continue
    fi

    update_repo $repo
done

git add -f $PROPOSALS_DIR
git diff --quiet --cached || git commit -m "Update proposals' tests"
