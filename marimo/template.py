import marimo

__generated_with = "0.6.14"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    import json
    from marimo import cli_args

    return cli_args, json, mo


@app.cell
def __(cli_args):
    args = cli_args().to_dict()

    for key, value in args.items():
        print(key, value, type(value))

    return args, key, value


if __name__ == "__main__":
    app.run()
