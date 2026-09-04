# Shared chart examples

Every executable example emits the same backend-neutral `sum.chart/1` JSON contract.  The output can be rendered as text or as a Pygame window without changing the producing language.

Examples:

```bash
python chart.py | sumchart --backend=tui
python chart.py | sumchart --backend=gui

Rscript chart.R | sumchart --backend=tui
Rscript chart.R | sumchart --backend=gui

bash chart.sh | sumchart --backend=tui
bash chart.sh | sumchart --backend=gui

cc chart.c -o chart-c && ./chart-c | sumchart --backend=tui
cc chart.c -o chart-c && ./chart-c | sumchart --backend=gui

c++ chart.cpp -o chart-cpp && ./chart-cpp | sumchart --backend=tui
c++ chart.cpp -o chart-cpp && ./chart-cpp | sumchart --backend=gui

node chart.js | sumchart --backend=tui
php chart.php | sumchart --backend=tui
ruby chart.rb | sumchart --backend=tui

sumbasic --run chart.bas | sumchart --backend=tui
sumx --plain --run chart.prg | sumchart --backend=tui
```

Replace `--backend=tui` with `--backend=gui` for the graphical renderer.  `sumchart` belongs to the backend-neutral `sumUI` package and dynamically loads the requested installed backend.

The HTML example embeds the same contract for browser/document-oriented work; its JSON can be passed to `sumchart` by any host or script that extracts the `<script>` object.

<p align=center><b>- oOo -<b></p>

<p align=center><b>- oOo -</b></p>
