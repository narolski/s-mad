"""glintr100 (ArcFace R100, Glint360K) embeddings through the registered X3 / A46-D2 route: prep_eval.kps (unchanged,
pinned) -> insightface norm_crop -> a2f_common.embed_crops('glint') (pinned). Measurement only; no image is written."""
import numpy as np

import ar1_common as K

_PE = _A2F = None


def _mods():
    global _PE, _A2F
    if _PE is None:
        K.add_paths(K.MC)
        _PE = K.load_module(K.MC / "smadcvpr/prep_eval.py", "prep_eval")
        _A2F = K.load_module(K.A2F_DIR / "a2f_common.py", "a2f_common")
    return _PE, _A2F


def embed_images(imgs):
    """list of BGR uint8 arrays -> (emb n x 512 float32 L2-normalised, found bool n)."""
    import cv2  # noqa: F401
    from insightface.utils.face_align import norm_crop
    PE, A2F = _mods()
    crops, found = [], []
    for img in imgs:
        kp = PE.kps(img)
        if kp is None:
            crops.append(np.zeros((112, 112, 3), np.uint8))
            found.append(False)
        else:
            crops.append(norm_crop(img, kp))
            found.append(True)
    emb = np.asarray(A2F.embed_crops("glint", crops), np.float32)
    return emb, np.array(found)


def embed_paths(paths, chunk=512, log=None):
    import cv2
    E, F = [], []
    for i in range(0, len(paths), chunk):
        e, f = embed_images([cv2.imread(str(p)) for p in paths[i:i + chunk]])
        E.append(e)
        F.append(f)
        if log:
            log(f"embedded {min(i + chunk, len(paths))}/{len(paths)}")
    return np.concatenate(E), np.concatenate(F)
