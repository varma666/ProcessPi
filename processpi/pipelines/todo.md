# ProcessPI - Pipelines Module TODO

## ✅ Phase 1 (Current Framework)
- [x] Define `Pipe`, `Fitting`, `PipelineNetwork` classes.
- [x] Support series & parallel pipeline connections.
- [x] Store nodes with elevations.
- [x] Basic schematic using `networkx + matplotlib`.

---

## 🔄 Phase 2 (Enhancements - Next)
- [ ] Add auto-sizing rules (velocity, pressure drop).
- [ ] Expand material database (CS, SS, PVC, HDPE, Copper).
- [ ] Add standard fittings library with default K-values.
- [ ] Elevation handling → automatic static head calculation.

---

## 🎨 Phase 3 (Visualization Improvements)
- [ ] PFD-style schematic with unit symbols (pump, HX, valve).
- [ ] Flow direction arrows on diagram.
- [ ] Color-coded pipes by diameter/material.
- [ ] Interactive visualization with Plotly or PyVis.

---

## ⚙️ Phase 4 (Advanced Features)
- [ ] Automatic line numbering (e.g., P-101A, P-101B).
- [ ] Branch handling with flow split ratios.
- [ ] Hydraulic balancing for parallel networks.
- [ ] Pump integration (head & power calculation).
- [ ] Control valve sizing (ΔP and Cv).

---

## 📤 Phase 5 (Integration & Export)
- [ ] Export schematic to PNG/PDF.
- [ ] Export network data to Excel/JSON.
- [ ] GUI integration (web/desktop ProcessPI app).
- [ ] Rule-based design checks (velocity & ΔP limits).
