# VIS2 — niezależny postreview rzeczywistego smoke

2026-11-14. Recenzent: training_contribution, inny niż autor. **PASS_ALL3_TECHNICAL_SMOKE_ONLY**. Wszystkie trzy wymagane modele ukończyły exact smoke; nie znaleziono technicznego blockera dla osobnej decyzji root o pełnym etapie. Ten raport sam nie uruchamia ani nie autoryzuje full/render.

Zakres prywatnego odczytu wynika z ROOT_SMOKE_RELEASE SHA256 `c745033069b983b02060a6798621c2af679d7a04a7da2dfa3838d92bc247fc58`, jawnie dopuszczającego OTHER technical numeric smoke postreview. Source commit `29da6d932c199e9f2ef0dd923cce0dabdc1fe0e0` i release commit `4121fd9470a73156d429ad01ec87dd9dec3e4da6` zweryfikowano przez porównanie bajtów przypiętych plików. Inventory/source/prereg/independent pre-review hashe zgodne. Nie otwierano fotografii, wag, modeli, sealed data; nie wykonano inference, transformacji, powtórzenia readera ani nowych statystyk.

Driver `/mnt/t7/smad_next/coordination_20261114/vis2_smoke_execution_20261114T215734Z` zakończył pracę22:02:09.723317Z jako ALL_COMMANDS_EXITED_ZERO. Trzy natywne exit0, serial order SelfMAD→A→B i exact argumenty smoke/model/timeout są zgodne. STARTED potwierdza brak competing compute apps i ≥50GiB T7; source driver trzyma mutex podczas całego szeregu. Każdy stdout ma exact COMPLETE smoke48, wszystkie stderr są puste. Nie było timeoutów, partial failures lub brakujących modeli; żaden model/warunek nie został odrzucony. Brak FAILED.json; to wspierane kompletnymi RESULT i exit0, nie wnioskowane z samej nieobecności pliku błędu.

| Model | Odpowiedzi | Native exit | Max baseline anchor residual | Worker time | RESULT SHA256 |
|---|---:|---:|---:|---:|---|
| selfmad_hrnet_w18 | 48/48 | 0 | 0.0 | 3.704467s | `f8145aaaf6cb50163d5ce8df5ade80d93d5adfa099c30c12194db4bbb30413ca` |
| A403 (CLI A) | 48/48 | 0 | 0.0 | 4.498788s | `0c427212467de41bfb3bd1ff19b788e628167b64782b0ba0456c8a02d434dbe8` |
| B403 (CLI B) | 48/48 | 0 | 0.0 | 3.975267s | `d2ae342dfc3f0538bddf9dd93b9f734f771ae3e38915d33474463453df00b01c` |

Łącznie144/144 finite occlusion responses, dokładnie4 wejścia×2fills×6 komórek na model. Sprawdzono kolejność, unikalność, cały iloczyn warunków, native coords/row/col/area4096 oraz równanie Δz=zocc−zbaseline dla każdej odpowiedzi. Wszystkie4 progress JSON/model są dokładnymi odpowiednimi częściami RESULT. Każdy SHA256.json rehashuje STARTED, RESULT i4 progress pliki poprawnie. Wszystkie12 zapisanych baseline scores są dokładnie równe wcześniej dopuszczonym VIS1 anchors (mocniej niż wymagane≤1e−5).

Rzeczywiste metadane potwierdzają NVIDIA GB10, torch2.12.1+cu130, CUDA13.0, SelfMAD384 i A/B224, batch1, float32/no autocast/no gradients/noTTA oraz oba TF32off. Tensor-equality canonical↔memory preprocessing, repeat/no-op≤1e−5 i eval/frozen są obligatoryjnymi bramkami przypiętego worker control-flow przed COMPLETE. Worker nie serializuje osobnych residuals tych trzech checks, więc recenzja **nie przedstawia ich jako niezależnie powtórzonej inferencji**. Nie gwarantuje również deterministyczności wszystkich kernelów przy cudnn.deterministic=False.

Do48 odpowiedzi/model dochodzi12 baseline/repeat/no-op forwardów, czyli60/model i180 łącznie w smoke. Timingi to zapisany czas worker, nie pełny resource accounting; natywne procesy trwały około4.40/5.59/4.95s. Nie służą do zmiany merytorycznego zakresu lub wyboru modeli.

Komórki smoke są wyłącznie sześcioma prospektywnie wybranymi pozycjami, nie kompletną mapą8×8. Nie oceniano atrakcyjności/znaku efektów, nie tworzono map ani nie wybierano przykładów. Test potwierdza techniczną ścieżkę, nie przyczynowe cue/identity attribution, benchmark bias, przewagę metody lub naprawę ranking NOT_QUALIFIED/5FAIL. Fotografie genuine nie mają splice seam mask; native/history nadal różnią się także kadrem/alignment.

Towarzyszący `INDEPENDENT_SMOKE_POSTREVIEW_CHECKS_20261114.json` SHA256 `4efd309431f197d2551607bb93f867f7e30018cd53df33982c629776e772e66e` zawiera pełne piny i liczniki kontroli. Zachować smoke namespace i wszystkie144 odpowiedzi. Root może wydać **osobny** exact full release związany z tym raportem i niezmienionymi source/input/runtime gates:512 odpowiedzi/model, wszystkie3 modele, bez selekcji. Full measurement, późniejsza interpretacja numeric oraz prywatny overlay/render mają odrębne zgody. Publication/rights/501 extension pozostają HOLD; żywy manuskrypt niezmieniony.
