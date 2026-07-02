# Changelog

## 0.1.0 (2026-07-02)


### Features

* add expected field to expectations schema ([#261](https://github.com/WebAssembly/wasi-testsuite/issues/261)) ([26c9d40](https://github.com/WebAssembly/wasi-testsuite/commit/26c9d4017ebc9d09d931707437932192df3f043d))
* add initial Buck2 infra for WASI tests ([c9e13c7](https://github.com/WebAssembly/wasi-testsuite/commit/c9e13c712fd86933ce6961a0b4cfdbdd1bf3e1e3))
* add p3 stdout flush test ([#263](https://github.com/WebAssembly/wasi-testsuite/issues/263)) ([84d6cbd](https://github.com/WebAssembly/wasi-testsuite/commit/84d6cbdef1aa7e93fde0ea8fd42c748f08806ff7))
* add support for pywasm runtime ([56a3c3e](https://github.com/WebAssembly/wasi-testsuite/commit/56a3c3ef153a1f8e743041b1b8e05ae2ce9e9847))
* add support for wizard engine ([ad174d5](https://github.com/WebAssembly/wasi-testsuite/commit/ad174d5c7f1291ad18fb28c2a105f75bd0c3eea4))
* added bottleneck for limiting test builds ([81576bb](https://github.com/WebAssembly/wasi-testsuite/commit/81576bb0429076ffff9a14bb187b3928b03a13ba))
* added prettier codestyle for ts scripts ([e353206](https://github.com/WebAssembly/wasi-testsuite/commit/e35320620d1f61c77f64a17dfd1d00a878c52d5a))
* **buck2:** add extra wasi runtime coverage ([#235](https://github.com/WebAssembly/wasi-testsuite/issues/235)) ([1580dd8](https://github.com/WebAssembly/wasi-testsuite/commit/1580dd890f3989dccd1d32559d3284ff99fe6ab6))
* **buck2:** add jco runtime ([#238](https://github.com/WebAssembly/wasi-testsuite/issues/238)) ([5fd51c2](https://github.com/WebAssembly/wasi-testsuite/commit/5fd51c2477e5aba6bcc448328e28f8a6dca7738a))
* **buck2:** add language specific lintes and formatters ([#259](https://github.com/WebAssembly/wasi-testsuite/issues/259)) ([4fcde9c](https://github.com/WebAssembly/wasi-testsuite/commit/4fcde9ce4888830461542af9b9cffa2904987290))
* **buck2:** buckify all the tests ([#233](https://github.com/WebAssembly/wasi-testsuite/issues/233)) ([d1c60b1](https://github.com/WebAssembly/wasi-testsuite/commit/d1c60b16b33e4dd28286ec6fc51dce092d0ab69d))
* **buck2:** pin reindeer and move reindeer config to third-party ([#239](https://github.com/WebAssembly/wasi-testsuite/issues/239)) ([6da1977](https://github.com/WebAssembly/wasi-testsuite/commit/6da197746fdc895a989652d5d86e385e6f6e7dd0))
* **buck2:** remove custom python based build system ([#246](https://github.com/WebAssembly/wasi-testsuite/issues/246)) ([5206582](https://github.com/WebAssembly/wasi-testsuite/commit/52065826adff3180cc449c7acb98e5ea805fd71e))
* **buck2:** use hermetic rust ([#253](https://github.com/WebAssembly/wasi-testsuite/issues/253)) ([92d8a37](https://github.com/WebAssembly/wasi-testsuite/commit/92d8a370f1fb11c5929ce3c87b2a149cd8c0fdfa))
* **ci:** use buck2 for daily ci tests ([#237](https://github.com/WebAssembly/wasi-testsuite/issues/237)) ([7876510](https://github.com/WebAssembly/wasi-testsuite/commit/787651026aaa1991501a1fd5d528eb5a749d1014))
* enable easier single test debugging ([#251](https://github.com/WebAssembly/wasi-testsuite/issues/251)) ([efad45c](https://github.com/WebAssembly/wasi-testsuite/commit/efad45c8a4a492247cdb863c83067987afe74d47))
* vove wasi p3 parent symlink setup into tests ([#232](https://github.com/WebAssembly/wasi-testsuite/issues/232)) ([72757ea](https://github.com/WebAssembly/wasi-testsuite/commit/72757ea565cce969ca73b0895a52ecfd220fbf0c))
* **wasip3:** update to 0.3.0-rc-2026-01-06 ([f13976f](https://github.com/WebAssembly/wasi-testsuite/commit/f13976fec4d8ba72340c646383f76cb6cb257c93))


### Bug Fixes

* add 'out' attr to colorama download ([83e3715](https://github.com/WebAssembly/wasi-testsuite/commit/83e37159161dc75cd28c5c50bf7fcc4a9a163621))
* added prettierrc and fixed prettier command ([70fc310](https://github.com/WebAssembly/wasi-testsuite/commit/70fc3109ed2a13e12e40453a70618c51e0a9573c))
* address code review feedback ([414423b](https://github.com/WebAssembly/wasi-testsuite/commit/414423b00e470278b6b35c2a2b4cc0947c93efc8))
* avoid double slash in request url ([#236](https://github.com/WebAssembly/wasi-testsuite/issues/236)) ([8d7c249](https://github.com/WebAssembly/wasi-testsuite/commit/8d7c249d070b2fd7c4adf99730266f5f9bfebe13))
* avoid following symlinks when cleaning up test output ([#252](https://github.com/WebAssembly/wasi-testsuite/issues/252)) ([955fc78](https://github.com/WebAssembly/wasi-testsuite/commit/955fc780f869f563e75ab47a4396ba4d35e7b2da))
* **build:** add colorama dep to test runner ([f64f3e6](https://github.com/WebAssembly/wasi-testsuite/commit/f64f3e6fda9c4079a2e70f391a59c52227a401ba))
* do not use posix on shlex.split windows path ([e6116ca](https://github.com/WebAssembly/wasi-testsuite/commit/e6116ca5aa176a0cbb67013eaa4aa3af779efba0))
* fixed erroring out if no files found ([fcd20fa](https://github.com/WebAssembly/wasi-testsuite/commit/fcd20fa51edeb7b66e361dd23bbfd582e1f98e87))
* jco 1.24 with 0.3.0 ([#262](https://github.com/WebAssembly/wasi-testsuite/issues/262)) ([49faa6a](https://github.com/WebAssembly/wasi-testsuite/commit/49faa6a3c78e772c644a075bb6550b6758657f89))
* **p3:** use http types ([99ceffe](https://github.com/WebAssembly/wasi-testsuite/commit/99ceffe6a17ef4f18378a3eaba04c579169af53f))
* **p3:** use http types ([167b307](https://github.com/WebAssembly/wasi-testsuite/commit/167b307fff32ed02918836798fce5878142ffdb8))
* publish job ([#247](https://github.com/WebAssembly/wasi-testsuite/issues/247)) ([63feaeb](https://github.com/WebAssembly/wasi-testsuite/commit/63feaeb0e6f61906261f017cab7e5213f6c0d1b0))
* repair broken link ([6d23953](https://github.com/WebAssembly/wasi-testsuite/commit/6d23953611388debaf29db355e8b4c9229d77174))
* **wasip3:** replace rc with 0.3.0 release ([6d988f4](https://github.com/WebAssembly/wasi-testsuite/commit/6d988f41293039cb89d8fde083d44026c73ec75a))
* **wasip3:** temp skips for jco/wasmtime ([df505dc](https://github.com/WebAssembly/wasi-testsuite/commit/df505dc8f9cfe9f3ad42a7341d7e5233f68b0719))


### Miscellaneous Chores

* release 0.1.0 ([#258](https://github.com/WebAssembly/wasi-testsuite/issues/258)) ([d27c53f](https://github.com/WebAssembly/wasi-testsuite/commit/d27c53ff402be0900b1338214cca77418182a90d))
