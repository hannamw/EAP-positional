#%%
from pathlib import Path 

import numpy as np
import torch
from transformer_lens import HookedTransformer
from einops import einsum, rearrange
import matplotlib.pyplot as plt

from greater_than_dataset import get_prob_diff, YearDataset, get_valid_years
from graph import Graph, InputNode, LogitNode, AttentionNode, MLPNode
from attribute import attribute_vectorized

from attribute_vectorized import attribute_vectorized as ave
#%%
model_name = 'EleutherAI/pythia-160m'
model = HookedTransformer.from_pretrained(model_name)
model.cfg.use_split_qkv_input = True
model.cfg.use_attn_result = True
model.cfg.use_hook_mlp_in = True
#%%
def batch(iterable, n:int=1):
   current_batch = []
   for item in iterable:
       current_batch.append(item)
       if len(current_batch) == n:
           yield current_batch
           current_batch = []
   if current_batch:
       yield current_batch

ds = YearDataset(get_valid_years(model.tokenizer, 1100, 1800), 1000, Path("potential_nouns.txt"), model.tokenizer)

clean = list(batch(ds.good_sentences, 9))
labels = list(batch(ds.years_YY, 9))
corrupted = list(batch(ds.bad_sentences, 9))

input_length = 1 + len(model.tokenizer(ds.good_sentences[0])[0])
prob_diff = get_prob_diff(model.tokenizer)

# %%
# Instantiate a graph with a model and the length of the data
g = Graph.from_model_positional(model, input_length)
# Attribute using the model, graph, clean / corrupted data (as lists of lists of strs), your metric, and your labels (batched)
attribute_vectorized(model, g, clean, corrupted, prob_diff, labels)
# Apply a threshold
g.apply_threshold(0.011, absolute=False)
g.prune_dead_nodes(prune_childless=True, prune_parentless=False)
gz = g.to_graphviz()
gz.draw('graph_vectorized.png', prog='dot')

# %%
# Instantiate a graph with a model and the length of the data
g2 = Graph.from_model_positional(model, input_length)
# Attribute using the model, graph, clean / corrupted data (as lists of lists of strs), your metric, and your labels (batched)
ave(model, g2, clean, corrupted, prob_diff, labels)
# Apply a threshold
g2.apply_threshold(0.011, absolute=False)
g2.prune_dead_nodes(prune_childless=True, prune_parentless=False)
gz2 = g2.to_graphviz()
gz2.draw('graph_vectorized2.png', prog='dot')
# %%
