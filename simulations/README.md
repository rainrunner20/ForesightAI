# Echo Chamber Lab: two implementations, one purpose

The **tested Python agent model** is the source of synthetic discussion posts fed to the LLM experiment. NetLogo is an optional teaching/demo counterpart, not a validated production data source.

## Python model (recommended, integrated)

From the repository root:

```powershell
python -m foresight_ai.cli --provider mock --seed 733 --agents 120 --fact-checkers 0.15 --posts 16 --output outputs/demo.json
python -m http.server 5173 --directory web
```

Open the dashboard, select **Experiments → Import results JSON**, choose `outputs/demo.json`, then open **Diffusion Lab**. Use the Back/Next controls to step through actual *synthetic simulator* frames. These are real simulation outputs, not observed social behavior or LLM findings. You can use `--provider ollama` for actual model responses.

### Vary one factor at a time

Run repeated experiments with different `--fact-checkers` values (e.g. `0`, `0.15`, `0.40`) and the same `--seed`, claim set and model. This gives a pedagogical sensitivity analysis; this model is **not calibrated** to a real social network.

## NetLogo (optional source prototype)

`echo_chamber.nls` contains NetLogo 6-style source. Make a **blank NetLogo model**, paste the file into the Code tab and create two buttons named `setup` and `go` (with `go` set to forever). Add monitors for `rumor-reach` and `checked-count` if desired. Change the three initial values under `setup` to experiment with population size, fact-checkers and sharing probability. The NetLogo file is an optional reference and has **not been executed or cross-validated here**.

The Python and NetLogo variants follow similar ideas but have different edge sampling details. Their outputs must not be treated as numerically equivalent without a cross-validation study.
