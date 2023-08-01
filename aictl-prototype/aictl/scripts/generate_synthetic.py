import pandas as pd
from uuid import uuid4

if __name__ == "__main__":
    df = pd.read_csv("data/ci-clean.csv")
    cols = df.columns.tolist()
    rows = df.to_dict("records")
    trows = []
    for row in rows:
        # SeedId	SynthId	UtteranceIndex	Utterance	Role	Type	SynthesizedBy	SynthesisTime
        synth_id = str(uuid4())
        if not isinstance(row["Category"], type("hello")):
            continue
        for i, colname in enumerate(["Generated Prompts", "Response"]):
            trows.append(
                {
                    "SeedId": "NA",
                    "SynthId": synth_id,
                    "UtteranceIndex": str(i),
                    "Utterance": row[colname],
                    "Role": ["User", "AI"][i],
                    "Type": ["query", "api_call"][i],
                    "SythesizedBy": "Suriyadeepan Ramamoorthy",
                    "SynthesisTime": "NA",
                    "Category": row["Category"],
                }
            )
        # print(trows)

    df = pd.DataFrame(trows)
    print(df)
    df.to_csv("data/ci-synthetic.csv", index=False)
