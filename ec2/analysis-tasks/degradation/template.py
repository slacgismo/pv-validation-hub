"""
empty prototype.
"""

import marimo

app = marimo.App()


@app.cell
def __(json, mo, pd):

    def create_df_from_cli_args():
        args = mo.cli_args().to_dict()
        data = args.get("results_df")
        rows = []
        for row in data:
            rows.append(json.loads(row))

        df = pd.DataFrame.from_records(rows)
        return df

    return (create_df_from_cli_args,)


if __name__ == "__main__":
    app.run()
