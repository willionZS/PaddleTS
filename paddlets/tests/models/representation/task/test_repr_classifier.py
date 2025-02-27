# !/usr/bin/env python3
# -*- coding:utf-8 -*-
 
from base64 import encode
import pandas as pd
import numpy as np
import shutil
 
import unittest
from unittest import TestCase
 
from paddlets import TimeSeries, TSDataset
from paddlets.models.representation.task.repr_classifier import ReprClassifier
from paddlets.models.representation import TS2Vec, CoST
from paddlets.datasets.repository import get_dataset, dataset_list
from paddlets.utils import backtest
from paddlets.transform.sklearn_transforms import StandardScaler
from paddlets.metrics import MAE
 
from sklearn.svm import SVC
 
 
class TestReprCLassifier(TestCase):
    def setUp(self):
        super().setUp()
        def gen_data():
            target = TimeSeries.load_from_dataframe(
                pd.DataFrame(
                    np.random.randn(20, 1).astype(np.float32),
                    index=pd.date_range("2022-01-01", periods=20, freq="15T"),
                    columns=["a1"]
                ))
    
            observed_cov = TimeSeries.load_from_dataframe(
                pd.DataFrame(
                    np.random.randn(20, 2).astype(np.float32),
                    index=pd.date_range("2022-01-01", periods=20, freq="15T"),
                    columns=["b", "c"]
                ))

            static_cov = {"f": 1., "g": 2.}
            # multi target
            return TSDataset(target, observed_cov, None, static_cov)
        self.ts1 = [gen_data() for i in range(20)]
        self.ts2 = [gen_data()  for i in range(10)] 
        self.labels1 = np.random.randint(low=0,high=3,size= 20)
        self.labels2 = np.random.randint(low=0,high=3,size= 10)
        self.test_init()   
    
    def test_init(self):
        # case1
        ts2vec_params = {"segment_size": 20,  
                         "repr_dims": 10,
                         "batch_size": 4,
                         "max_epochs": 1}
        self.model1 = ReprClassifier(
                                repr_model=TS2Vec,
                                repr_model_params=ts2vec_params)
 

        # case2
        ts2vec_params = {"segment_size": 20,  
                         "repr_dims": 10,
                         "batch_size": 4,
                         "max_epochs": 1}
        self.model2 = ReprClassifier(
                                repr_model=TS2Vec,
                                repr_model_params=ts2vec_params,
                                downstream_learner= SVC(probability=True)
                                )

        # case3
        ts2vec_params = {"segment_size": 20,  
                         "repr_dims": 10,
                         "batch_size": 4,
                         "max_epochs": 1}
        self.model3 = ReprClassifier(
                                repr_model= CoST,
                                repr_model_params=ts2vec_params,
                                downstream_learner= SVC(probability=True)
                                )

    def test_fit_predict(self):
        #model1
        self.model1.fit(self.ts1,self.labels1)
        res = self.model1.predict(self.ts1)
        res = self.model1.predict_proba(self.ts1)

        self.model1.fit(self.ts2,self.labels2)
        res = self.model1.predict(self.ts2)
        res = self.model1.predict_proba(self.ts2)
        assert (len(res) == 10)

        #model2
        self.model2.fit(self.ts1,self.labels1)
        res = self.model2.predict(self.ts1)
        res = self.model2.predict_proba(self.ts1)
        print(self.labels1, res)
        self.model2.fit(self.ts2,self.labels2)
        res = self.model2.predict(self.ts2)
        res = self.model2.predict_proba(self.ts2)
        assert (len(res) == 10)
        
        #model3
        self.model3.fit(self.ts1,self.labels1)
        res = self.model3.predict(self.ts1)
        res = self.model3.predict_proba(self.ts1)
        self.model3.fit(self.ts2,self.labels2)
        res = self.model3.predict(self.ts2)
        res = self.model3.predict_proba(self.ts2)
        assert (len(res) == 10)


    def test_save_and_load(self):
        self.model1.fit(self.ts1, self.labels1)
        #model1
        self.model1.save(path="/tmp/test2/")
        model1 = self.model1.load(path="/tmp/test2/")
        import shutil
        shutil.rmtree("/tmp/test2/")
        predictions = model1.predict(self.ts1)
        assert (len(predictions) == 20)

