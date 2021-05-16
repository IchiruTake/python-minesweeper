# python-minesweeper
[Del] A self-built python game designed by HCMIU students: AI-solver (PyTorch/TensorFlow), code-solver, GUI, etc ...


Coding Style:
+ config.py: Where image location is tracked up either by directory or function
(1): If there are many images with non-consistent in size: "Key": str and "get_size": bool 
(2): If there are many images with consistent in size: "Key": Union[str, int]
(3): If there is one image: "get_size": bool 
