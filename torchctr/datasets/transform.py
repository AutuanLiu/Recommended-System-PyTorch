from typing import List, Union

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from torch.utils.data import DataLoader

from .data import RecommendDataset
from .utils import DataInput, DataMeta, FeatureDict, defaults


def sparse_feature_encoding(data: pd.DataFrame, features_names: Union[str, List[str]]):
    """Encoding for sparse features."""

    if not features_names:
        return None
    nuniques = []
    for feat in features_names:
        lbe = LabelEncoder()
        data[feat] = lbe.fit_transform(data[feat])
        nuniques.append(len(lbe.classes_))
    data_meta = DataMeta(data[features_names].values, features_names, nuniques)
    return data_meta


def sequence_feature_encoding(data: pd.DataFrame, features_names: Union[str, List[str]], sep: str = ','):
    """Encoding for sequence features."""

    if not features_names:
        return None
    data_value, nuniques = [], []
    for feature in features_names:
        corpus = [' '.join(str(x).strip().split(sep=sep)) for x in data[feature]]
        # vocab = set.union(*[set(x.split(' ')) for x in corpus])
        # vec = CountVectorizer(vocabulary=vocab)
        # multi_hot = vec.transform(data[feature])
        vec = CountVectorizer(token_pattern=r'(?u)\b[\w\']+\b')
        multi_hot = vec.fit_transform(corpus)
        data_value.append(multi_hot.toarray())
        nuniques.append(len(vec.vocabulary_))
        # to index
        # ret, offsets, offset = [], [], 0
        # for row in data[feature]:
        #     offsets.append(offset)
        #     row = row.split(sep) if isinstance(row, str) else str(row).split(sep)
        #     ret.extend(map(lambda word: vec.vocabulary_[word], row))
        #     offset += len(row)
        # data_value.append(ret)
    data_meta = DataMeta(np.hstack(data_value), features_names, nuniques)
    return data_meta


def dense_feature_scale(data: pd.DataFrame, features_names: Union[str, List[str]], scaler_instance=None):
    """Scaling for sparse features."""

    if not features_names:
        return None, None
    scaler = scaler_instance if scaler_instance else StandardScaler()
    scaler = scaler.fit(data[features_names])
    data[features_names] = scaler.transform(data[features_names])
    data_meta = DataMeta(data[features_names].values, features_names)
    return data_meta, scaler


def fillna(data: pd.DataFrame, features_names: Union[str, List[str]], fill_v, **kwargs):
    """Fill Nan with fill_v."""

    data[features_names] = data[features_names].fillna(fill_v, **kwargs)
    return data


def make_datasets(data: pd.DataFrame, features_dict=None, sep=',', scaler=None):
    """make dataset for df.
    
    Args:
        data (pd.DataFrame): data
        features_dict (FeatureDict): instance of FeatureDict. Defaults to None.
        sep (str, optional): sep for sequence. Defaults to ','.
        scaler: sacler for dense data.
    """

    sparse = sparse_feature_encoding(data, features_dict.sparse_features)
    dense, s = dense_feature_scale(data, features_dict.dense_features, scaler_instance=scaler)
    sequence = sequence_feature_encoding(data, features_dict.sequence_features, sep=sep)
    print('Making dataset Done!')
    return DataInput(sparse, dense, sequence), s


def make_dataloader(input: DataInput, targets=None, batch_size=64, **kwargs):
    dataset = RecommendDataset(input, targets)
    return DataLoader(dataset, batch_size=batch_size, **kwargs)
