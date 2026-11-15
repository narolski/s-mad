# VIS2 layout_v2 — niezależna recenzja źródłowa układu

2026-11-14. Recenzent training_contribution, inny niż autor. **GO_EXACT_LAYOUT_V2_SOURCE**. Nowy prywatny grant root oraz osobny actual12-page print review nadal wymagane; ten dokument nie pozwala jeszcze renderować ani prezentować rzeczywistych zdjęć/map.

Związane piny: source manifest `9ce196b3d0e53c58c0dedb0f182675222bb5c3ec2dd96eed07308453aeb40604`; renderer `71107b893eb144fc2bd9f45c6cb41115aed9ec942becc079e58fbab74d3a5e5f`; CONFIG_MAC `a083f9e251367606604344c3def51bc13708d16110ff4ae5c449c399195c8180`; delta `85236d6605ab00cf1c4e9c11b8d8c412fa30920c8913936d610b3705a6cf8c22`. Sprawdzono hashe wszystkich trzech plików źródłowych po immutable handoff. Stary v1r1 zachowany, jego actual322mm pack nie był otwierany w tej recenzji.

## Wykonane kontrole

- Bundled Python/ReportLab4.4.9:14 contract tests PASS (0.006s),4 finalization/alpha/E2E tests PASS (0.108s), bez skip. Zachowano wszystkie wcześniejsze18 przypadków, z aktualizacją oczekiwanej geometrii58mm/≤279.4mm/min8.2pt. Finalization nadal sprawdza3072 records,12 virtualSVG,2 mockPDF i6 pages/edition, L0/.45 alpha, history facts, writer create-only/NaN oraz FAILED zamiast COMPLETE po injected failure.
- Dodatkowy niezależny generated differential: uruchomiono mockowany cały main obu wersji v1r1 i layout_v2. Wszystkie3072 rekordy identyczne poza `x_mm`, `y_mm`, `edge_mm`; delta, limit, normalized value, kolor, hatching, alpha, model/input/fill/cell pozostały identyczne. Nie uruchomiono realnego PDF/SVG ani obrazu; sentinel grafiki tylko w pamięci, temporary generated JSON usunięte.
- Dodatkowo zastąpiono w lokalnym niezależnym harnessie uproszczone mock stringWidth **rzeczywistymi metrykami przypiętych Arial/Arial Bold**, bez zmiany zamrożonych źródeł. Oba generated E2E flows przechodzą rzeczywistą kontrolę szerokości wszystkich generowanych linii; exact credit strings z config mieszczą się przy8.2pt. To source/font-metrics check, nie actual photograph/print QA.

## Geometria i treść

Strona180×279.4mm fizycznie mieści się na Letter215.9×279.4 oraz A4210×297 bez skalowania treści. Źródłowe fotografie58×58mm: y24–82, x17–75 i105–163. Mapy58×58mm: y100–158 i173–231 w tych samych dwóch kolumnach; każda komórka7.25mm. Panelom pozostaje odstęp, brak nakładania źródeł/map; legend237–245, komentarze249–269, footer baseline275mm przy8.3pt, wewnątrz wysokości279.4. Min font8.2pt, baseline rawz9.4pt. Układ nie redukuje fontu dla zmieszczenia. Nie gwarantuje to obsługi marginesów każdego fizycznego drukownika; actual review ma użyć native180mm i kontrolować brak autoshrink/cropping.

Baseline pokazuje teraz tylko raw morph-oriented z, bez sigmoidu/probability. Jawny opis: większe z oznacza silniejsze wskazanie morph; czerwony=zasłonięcie podnosi z, niebieski=obniża. Δz nadal zocc−zoriginal. Grayscale zachowuje magnitude oraz negative hatch z opisem obniżenia wyniku. Wspólna skala512/model i różne skale modeli są jawne. Ograniczenia probability/causality, compound alignment/crop, brak szwu na genuine zdjęciach, credits i private/not publication label pozostają widoczne; history_facts nadal w manifest.

Nowy authorize check wiąże page width/height/photo_map_edge/minfont config z konkretnym źródłem. Source/data contract, input/result provenance, fixed all-model roster, geometry64×64 native pixels, two fills,512 numeric cells/model, zero/tinyL/no clipping, alpha fix, durable JSON helper i FAILED/COMPLETE behavior pozostają niezmienione względem zrecenzowanego v1r1. Nadal obowiązuje ograniczenie: helper fsync dotyczy JSON, nie crash-atomic gwarancji wszystkich grafik.

## Dyspozycja

Root może przygotować **nowy exact layout_v2 render grant**, wiążący ten review/source/config, poprzedni full numeric review `b9a6a9dd491dfd6f3189deef11855c367ccecbd6d61e8f77452d6c971b993d7c`, wszystkie3 full RESULT hashes i4 prywatne PNG oraz świeży output namespace. Nie nadpisywać starego322mm packa. Po wykonaniu: native exit/COMPLETE/noFAILED, hashes,3072 records oraz OTHER actual12-page color/grayscale/PDF/SVG print review, minimum8pt bez skali zmniejszającej.

W tej recenzji nie otwierano żadnych actual RGB/RESULT/renderów, nie było model/GPU/inference. Żywy manuskrypt niezmieniony. Źródłowa zmiana wizualna nie zmienia nauki, ranking NOT_QUALIFIED/5FAIL ani praw. Publication/likeness/consent/501 extension pozostają HOLD; GO nie jest actual private presentation approval.
