## Notebook text layer "autofix"
Jupyter's auto-formatter will try and interpret the RegEx string as in MathJax mode, corrupting RegEx strings (especially the parantheses) in the process.

If readers see RegEx strings (e.g. variables `pattern`) having no parantheses, manually replace them in-line with:
> `pattern = r"^9999.*$"` should be changed to `pattern = r"^\(99\).*$"`
> `r"^\d+\d+\s*"` should be changed to `r"^\(\d+\)\s*"`
before proceeding with interactive elements.

## Raw data
The VoteCast PUF ZIPs are 165 MB total; ~ 650 MB after decompression, exclusing redundant coding in non-CSV formats.

Run `python get_votecast.py` or follow the link below to download them directly from AP–NORC.

https://apnorc.org/wp-content/uploads/2021/05/AP-VoteCast-2020-Public-Use-Files.zip

https://apnorc.org/wp-content/uploads/2021/05/AP_VOTECAST_2024_GENERAL.zip

## 1-click setup
```bash
git clone https://github.com/Fiftyfour33/01909412-math70076-assessment-2.git
cd 01909412-math70076-assessment-2
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python data/get_votecast.py
jupyter notebook  # now all notebooks run
