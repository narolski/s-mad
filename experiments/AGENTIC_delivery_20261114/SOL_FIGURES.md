# Sol — figury wyjaśniające zachowanie modeli

Kontrola dokumentów i metadanych: **2026-11-14T16:39:54+01:00**, zegar gx10-c326. Status: **rzeczywiste wyniki OCC1 i kandydaty wydruku istnieją; niezależna recenzja wyników i wydruku nadal nie została znaleziona w pakiecie**. Nie przedstawiać panelu OCC1 jako gotowego dla użytkownika.

Ten follow-up nie uruchamia modeli, testów, renderowania, ponownego liczenia map ani odczytu plików score/NPZ. Nie otwarto payloadów kandydatów. Zweryfikowano dokumentację, obecność wskazanych artefaktów i istniejący raport kontroli SVG. Poniższe hashe są zapisanymi pinami wcześniejszego handoffu, nie nową walidacją zawartości map.

## Co już istnieje i nie wymaga ponownego liczenia

Pełny zapis: `/home/narolski/smad-next/experiments/OCC1_seam-surround-pilot_20261114/`. Wyniki trwałe: `/mnt/t7/smad_next/OCC1/20261114/`.

| Model | Zapisany stan | Artefakt |
|---|---|---|
| A, B, Sb — zamrożony seed 403 | Każdy: smoke PASS i pełne 1024 okluzje | `{A,B,Sb}_full/` |
| Oficjalny MixFaceNet-MAD | Smoke PASS i pełne 1024 okluzje | `mixfacenet_mad_smdd_full/` |
| Oficjalny SelfMAD, aligned-frame | Smoke PASS i pełne 1024 okluzje | `selfmad_hrnet_w18_full/` |
| Oficjalny MADation ViT-B/16 | Failed smoke: porównanie batch 1/batch 8; bez pełnego przebiegu/retry | `madation_vitb16_smoke/failure.json` |
| Oficjalny MADation ViT-L/14 | Failed smoke: CUDA OOM podczas model.to; bez pełnego przebiegu/retry | `madation_vitl14_smoke/failure.json` |

Razem: **5120 rzeczywistych pełnych okluzji**, 8 stałych wariantów wejścia, 2 stałe wypełnienia, 64 pozycje maski na model. Dodatkowo zachowano 320 widoków zakończonych smoke. Nie powielać pięciu pełnych przebiegów.

Każdy katalog `_full/` zawiera `raw_responses.npz`, `per_patch_scores.csv`, `result.json` i receipt startu. Na poziomie głównym są `baseline_scores.csv` (40 wierszy), `regional_effects.csv` (80 wierszy) i `paired_rung_effects.csv` (50 wierszy). Zapisany weryfikator autora sprawdził kompletność skończonych gridów, zgodność CSV/NPZ, delty, średnie regionalne i kontrasty sparowanych wariantów. **To kontrola autora, nie niezależna recenzja.**

Przypięte dowody:

- `NUMERICAL_OUTPUT_VERIFICATION.json`: `193ec7ff4c57353b8bc79486abaf7028ff7f37659e610e48b2c8ee4d8e8495d8`.
- `experiments/OCC1_seam-surround-pilot_20261114/ASTRA_PRERUN_REVIEW_20261114.md`: `e4494f0021934c90ff89f26348cf5ec9c073467893708060df4f633dab6ddb0f` — dotyczy przygotowania, nie późniejszych wyników.
- `PARENT_INTERNAL_RESEARCH_ADMISSION_20261114.json`: `9e1bd122966c6b9ac45984cdb3b6f0d9f25ba352d0e454ef6a48078270fd464c` — wyłącznie numeric-only, in-place, internal research.
- Szczegółowy handoff: `experiments/AGENTIC_delivery_20261114/FIGURES_OWNER_HANDOFF_20261114.md`, `5d9fbec1efa39093b4b28b3b4d6087dfd988fcae49a298fb334c4ee25c5ecb53`.

## Kandydaty wydruku gotowe do niezależnego oglądu

Używać **`/mnt/t7/smad_next/OCC1/20261114/numeric_print_v2/`**. Jest pięć plansz modelowych, każda w kolorze i grayscale oraz formatach PDF/SVG/PNG. Przykłady:

- `A_color.pdf` i `A_grayscale.pdf`;
- `Sb_color.pdf` i `Sb_grayscale.pdf`;
- `selfmad_hrnet_w18_color.pdf` i `selfmad_hrnet_w18_grayscale.pdf`.

To rzeczywiste mapy 8×8 zmian logitu dla S0/S3/S4, z zapisanymi bazowymi i okludowanymi logitami oraz średnimi regionalnymi. Bez zdjęć źródłowych i overlayów. Podświetlony P18 wybrano geometrycznie przed score. Skala jest wspólna w obrębie modelu dla wszystkich 8 wariantów i obu wypełnień; nie wygładzano map.

Zapisane QA: 180×210 mm, konfiguracja minimum 8 pt; wszystkie 10 rzeczywistych SVG mają minimalny rozmiar tekstu 8 w jednostkach strony. Przykładowy PDF ma potwierdzony rozmiar 180×210 mm. Autor obejrzał A color i SelfMAD grayscale. **Brakuje niezależnego oglądu całości w docelowym rozmiarze.** PyMuPDF był niedostępny; kontroli font-spanów PDF nie wykonano. Starszy `numeric_print/` ma nakładające się etykiety i pozostaje odrzuconą rewizją; nie wybierać go jako deliverable.

- `numeric_print_v2/FIGURE_MANIFEST.json`: `e44f8cf76ac4b810b14b3c54c63b36fcbf322c7f25302cf369a3e0b468b64272`.
- `numeric_print_v2/SVG_PRINT_SIZE_FONT_QA.json`: `c4ebad0e37f930cd162b407bd1e51a6ff07db696aead4ad90b9e6c2335034f31`.

## Pozostałe bramki

1. **Niezależna poprawność liczb i interpretacji.** Recenzent niebędący autorem ma odtworzyć delty/średnie/kontrasty z istniejących plików i uwzględnić wszystkie 7 dyspozycji modeli. Nie trzeba ponownie uruchamiać inference. W sprawdzonych rekordach znaleziono jedynie OCC1 prerun review, nie post-result GO.
2. **Niezależna czytelność wydruku.** Obejrzeć wszystkie pięć modeli w kolorze i grayscale przy 180 mm, porównać P18/legendy/colorbar z istniejącym outputem. Dopuszczalne są poprawki renderowania w nowej rewizji; nie zmieniać danych ani wygładzać odpowiedzi.
3. **Prawa do pokazania twarzy — osobno.** Obowiązujący release nie obejmuje eksportu oryginałów, obrazów po okluzji ani overlayów. Różnicę między aktualnymi warunkami Color FERET i starszą lokalną umową Gray opisuje README. Ten follow-up nie rozstrzyga nowej licencji. Można recenzować istniejące wykresy bez twarzy bez otwierania tej bramki.
4. **MADation B/L — brakujące mapy pozostają failure.** Dla B nie zapisano dokładnego wariantu/dysproporcji uruchamiającej błąd parity; przyczyna OOM L jest nieustalona. Nie dopowiadać diagnozy. `ASTRA_PLAN_OCC1_REQUEST_20261114.md` kieruje recovery do istniejącego rodzicielskiego `/root/astra_compute_unblock_plan`; nie tworzyć duplikatu ani ponawiać modeli bez nowego prospektywnego planu i release. Obecny pakiet nie dostarcza gotowego dodatkowego dispatchu OCC1.

## Następny krok, który można wykonać teraz

Przydzielić **jeden ograniczony niezależny przegląd istniejących wyników i wydruku v2**, bez nowych obliczeń GPU i bez źródłowych zdjęć. Wejścia: prereg/piny/admission/prerun review, weryfikator i receipts, pięć kompletnych outputów, dwa failed smokes, `numeric_print_v2/`. Wynik: osobne GO/GO_WITH_FIXES/NO_GO dla poprawności liczb, zakresu opisu i wydruku, z dokładnymi hashami recenzowanego pakietu. Bramka praw do zdjęć ma pozostać osobna.

Obowiązkowe zastrzeżenia recenzji/caption: Δz=z_occluded−z_original; ujemna delta oznacza mniej attack-like, nie zmianę błędu detekcji. Sigmoid to niekalibrowany score. Co najmniej 10% pola maski 64 px pokrywa wąski ring, więc maska usuwa również inne informacje z twarzy. Kontrole są zgodne tylko pod względem pola/kształtu, nie tekstury/pozycji. S4/S0 mają wspólne tło R2w4, a S3 tło R2w. Dwa wypełnienia nie eliminują artefaktów maski. Jeden stały development host nie uzasadnia efektu populacyjnego, lokalizacji przyczynowej ani poprawy metody.

Poprzedni pilot gradientowy FFHQ jest odrębnym, już recenzowanym artefaktem; jego private-display GO nie przenosi się na OCC1. Bieżący krok kończy się handoffem do recenzji, nie nową mapą, retry lub publikacją.
