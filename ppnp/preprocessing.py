import copy
import numpy as np


def gen_seeds(size=None):
    max_uint32 = np.iinfo(np.uint32).max
    return np.random.randint(
            max_uint32 + 1, size=size, dtype=np.uint32)


def exclude_idx(idx: np.array, idx_exclude_list):
    idx_exclude = np.concatenate(idx_exclude_list)
    return np.array([i for i in idx if i not in idx_exclude])


def known_unknown_split(idx, nknown=1500, seed=4143496719):
    rnd_state = np.random.RandomState(seed)
    known_idx = rnd_state.choice(idx, nknown, replace=False)
    unknown_idx = exclude_idx(idx, [known_idx])
    return known_idx, unknown_idx


def train_stopping_split(
        idx, labels, ntrain_per_class=20, nstopping=500, seed=2413340114):
    rnd_state = np.random.RandomState(seed)
    train_idx_split = []
    for i in range(max(labels) + 1):
        train_idx_split.append(rnd_state.choice(
                idx[labels == i], ntrain_per_class, replace=False))
    train_idx = np.concatenate(train_idx_split)
    stopping_idx = rnd_state.choice(
            exclude_idx(idx, [train_idx]),
            nstopping, replace=False)
    return train_idx, stopping_idx


def gen_splits(labels, idx_split_args, test=False):
    all_idx = np.arange(len(labels))
    known_idx, unknown_idx = known_unknown_split(
            all_idx, idx_split_args['nknown'])
    _, cnts = np.unique(labels[known_idx], return_counts=True)
    stopping_split_args = copy.copy(idx_split_args)
    del stopping_split_args['nknown']
    train_idx, stopping_idx = train_stopping_split(
            known_idx, labels[known_idx], **stopping_split_args)
    if test:
        val_idx = unknown_idx
    else:
        val_idx = exclude_idx(known_idx, [train_idx, stopping_idx])
    return train_idx, stopping_idx, val_idx
