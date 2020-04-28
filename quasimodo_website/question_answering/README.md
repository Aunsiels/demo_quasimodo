To generate the model used for question answering, download quasimodo, put
 it in this directory, and run:
 
 ```bash
python3 preprocessing.py quasimodo.tsv all_training_data.jsonl
```

This operation can take several hours to complete and it will generate a file
 classifier\_lr.pck.