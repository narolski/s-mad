# VIS2 v1 — niezależny pre-review źródeł

2026-11-14. Recenzent training_contribution, inny niż autor shortcut_visual_examples. **GO_SOURCE_FOR_ROOT_TECHNICAL_SMOKE_RELEASE**, wyłącznie dla exact Phase A i pod warunkami wykonawczymi poniżej. Nie jest to bieżąca zgoda wykonawcza, zgoda na full ani rendering. Nie znaleziono blokującego błędu źródłowego w zakresie tego audytu.

Związany pakiet: `src/VIS2/v1/SHA256SUMS` SHA256 `31ae2f57c2212c2ac85a90360753e9f20e5db98a6ba3e5c4a9dd5efaa686b0cb`; worker `49fac2668bce1c24e88a581a9ce38c16f6ec1b9e64b633cc7edaf61d1fb7068e`; INVENTORY `11316da9452632614dd85ae8cd659c7e363467a6f66590a8dc6b21125b1dfcf9`; prereg `14a8bc76d13b8f5a36a71d262642d6046ffc80d36621d04ea87bd9c3c666804b`.

## Sprawdzone

Przeczytano AGENTS/CONTINUE, HANDOFF.json, prereg, COMMANDS, inventory, print spec, worker i testy oraz wskazane rzeczywiste adaptery VIS1/common/a12_released. Nie otwierano fotografii, wag, modeli, nowych occlusion results ani zamkniętych benchmarków; brak wywołań GPU. Sprawdzono hashe dwóch plików źródłowych i25 przypiętych źródeł/provenance. Cztery wejściowe ścieżki/hashe porównano **wyłącznie jako metadane** z poprzednim VIS1 inventory. Wszystkie12 baseline anchors dokładnie zgadzają się z wcześniej dopuszczonymi zagregowanymi VIS1 RESULT. Nie ponownie liczono starych score'ów.

Rzeczywiste wywołanie CPU-generated `test_geometry.py` w zadeklarowanym izolowanym Pythonie: **6/6 PASS**, 0.007s. Fixture sprawdza pełne jednokrotne pokrycie8×8,4096 zmienionych pikseli, obie stałe0/128, zachowanie wejścia, znak toy-linear delta, odrzucanie niedozwolonych współrzędnych/fill, no-op, dtype/shape. To testy syntetyczne; nie stanowią testu realnego adaptera/modelu lub reprodukcji GPU.

## Mianowniki i źródłowa zgodność

- Phase A zawiera dokładnie42/56×native/history i modele `selfmad_hrnet_w18`, `A`, `B`. Etykiety A403/B403 w opisie oznaczają seed403; poprawne argumenty CLI to A/B. Nie włącza00010, Sb403 lub501.
- Smoke:4 wejścia×6 stałych komórek×2fills = **48 odpowiedzi/model**,144 łącznie. Full:4×64×2 = **512/model**,1536 łącznie. Każdy etap dodaje4×3 =12 forwardów baseline/repeat/no-op na model: technicznie60 forwardów smoke i524 full/model,180 i1572 dla całej trójki. Full ponownie mierzy warunki smoke zgodnie z prospektywnym planem, bez wyboru korzystnych komórek.
- Przed jakąkolwiek occlusion wszystkie4 oryginały przechodzą tensor-equality memoryprep↔canonical ImageItems, finite i1e−5 anchor/repeat/no-op. Geometry jest row-major64px w512RGBuint8, maskowanie przed modelowym resize. Delta ma znak `z_occluded−z_original`. Nie ma progu, p-value, CI ani decyzji klasyfikacyjnej.
- SelfMAD: rzeczywiste źródło ma HRNet-W18,384RGB[0,1], class1 morph minus class0 bona; A/B używają tego samego VIS1 loadera trainable-overlay/frozen-base oraz forward_logit. Piny obejmują metadane403/last, trainable weights i frozen CLIP base; worker sprawdza key sets. Batch1, eval, no_grad, wszystkie parametry frozen, float32, bez autocast/TTA, TF32off. PIL bilinear i RGBfloat32/255 odpowiadają przeczytanemu common loaderowi.
- Stałe RNG i kolejność czynią konstrukcję/plan deterministycznymi. `cudnn.deterministic=False` jest jawnie przypięte zgodnie z VIS1; **nie wolno opisywać tego jako gwarancji bitowej deterministyczności wszystkich occlusion kernelów**. Native anchors i repeat/no-op≤1e−5 są rzeczywistym gate, bez rozszerzania tolerancji.

## Gate wykonawczy: root musi zamknąć przed smoke

Nowy prywatny grant wiąże dokładne inventory/prereg/sourceSUMS, ten review/hash, distinct author/reviewer, source commit i jawne `phase=smoke`, models tylko wskazana trójka. Worker odrzuca legacy VIS1 grant; exige new_private_occlusion_transform_allowed=true, source_pixel_export_allowed=false i new_overlay_render_allowed=false. Owned source/input authority oraz release muszą być tracked i clean; każdy owned path jest porównywany z przypiętym source_commit. Commit źródłowy poprzedza commit grant, unikając samoodwołania.

Root osobno sprawdza brak konkurencyjnego GPU work, ≥50GiB rezerwyT7, świeże fixed namespaces, dokładny GB10/Python3.12.3/torch2.12.1+cu130/CUDA13.0 i package pins. Są to częściowo **zewnętrzne** warunki operacyjne, a nie wszystkie automatyczne checks workerowi. Runtime GPU/torch jest sprawdzany przez worker; nie ma CPU/H100 fallback. Nie wykonywano tych realnych warunków w tej recenzji. Root zachowuje stdout/stderr, natywny exit oraz timeout TERM/KILL15min/model. TERM/KILL może nie zapisać FAILED.json; nadrzędny receipt i brak kompletnego RESULT wtedy oznaczają failure/inconclusive, nigdy PASS. Nie uruchamiać automatycznego retry.

Worker rezerwuje stały namespace create-only przed model loading; JSON progress po każdym wejściu i RESULT są zapisywane z fsync, bez RGB/feature export. Błąd w trakcie inference pozostawia STARTED/FAILED/progress; nie usuwać częściowych wyników. Baseline/preprocessing checks są świadczone control-flow COMPLETE, a nie zapisanymi per-anchor residualami; independent smoke postreview musi uwzględnić to ograniczenie i związany kod.

**Full pozostaje HOLD:** osobny exact root full release i independent OTHER actual smoke postreview wszystkich trzech modeli (także failures) są konieczne. Kod wymaga przypiętego smoke_postreview przy full; semantyczne przyjęcie jego werdyktu i kompletności należy do root/review. Niniejszy dokument nie upoważnia do automatycznej promocji ani renderingu.

## Interpretacja i przyszły print review

Dwie fotografie genuine nie zawierają rzeczywistej splice seam/morphmask. To czułość na lokalne zasłonięcie, nie tożsamość przyczynowa, wykrycie szwu, przyczyna pięciu ranking FAIL lub dowód utility. Native/history różni się także alignment/crop/FOV; grid alignment nie jest anatomical correspondence. Obie stałe same tworzą artefakty, obie pozostają widoczne. Modele i przykłady mają możliwą ekspozycję, SelfMAD demonstration choice było post-hoc; brak niezależnej próby populacyjnej. Ranking NOT_QUALIFIED i5FAIL pozostają bez zmian.

Print spec jest adekwatnym **planem**, nie gotowym rendererem ani wynikiem:180mm/min8pt, pełne4inputs×2fills, wspólna symetryczna skala w obrębie modelu, bez interpolacji/clipping/percentile boost, grayscale magnitude+negative hatch. Renderer powinien jawnie obsłużyć L=0 bez sztucznego kontrastu. Actual print/overlay wymaga rzeczywistych numeric results, OTHER postreview i osobnego nowego render grant. Niczego nie wyrenderowano w tej recenzji. Prawa/publication/likeness/consent oraz501 extension pozostają **HOLD**; nie dziedziczą tej zgody.

Zalecenie: root może teraz przygotować nowy ściśle związany **technical smoke grant**, po commit/clean/runtime/resource checks, bez zmiany source lub scientific scope. Po trzech smoke'ach oddzielna ocena faktycznej reprodukcji i kompletności; żadnego pełnego etapu lub publikacyjnego claimu na podstawie samego source GO.
