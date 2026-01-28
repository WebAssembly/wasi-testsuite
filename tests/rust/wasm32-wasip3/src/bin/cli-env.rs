use test_wasm32_wasip3::cli::{export, exports::wasi::cli::run::Guest, wasi::cli::environment};

struct Component;
export!(Component);

fn test_get_environment() {
    let env = environment::get_environment();
    assert_eq!(
        env,
        vec![("foo".into(), "bar".into()), ("baz".into(), "42".into())]
    );
}

fn test_get_arguments() {
    let args = environment::get_arguments();
    assert_eq!(args, vec!["cli-env.wasm", "a", "b", "42"]);
}

fn test_get_initial_cwd() {
    let cwd = environment::get_initial_cwd();
    assert!(cwd.is_none());
}

impl Guest for Component {
    async fn run() -> Result<(), ()> {
        test_get_environment();
        test_get_arguments();
        test_get_initial_cwd();
        Ok(())
    }
}

fn main() {
    unreachable!()
}
