def generate_report(results, out_path=None):
    # placeholder: write or return a report
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(results))
    return {"report": results}
