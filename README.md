# python-minesweeper
Minesweeper is a single-player puzzle video game. The objective of the game is to clear a rectangular board containing hidden "mines" or bombs without detonating any of them, with help from clues about the number of neighboring mines in each field. 

![image](https://github.com/IchiruTake/python-minesweeper/blob/main/image/%5BTest%5D%20Image%20%231.png)

# Features:
- _Depth First Flow in Minesweeper_: Inherited from Depth First Search + Apply Mathematical Function + Expand to Boundary from Center to any positions. ---> Time Complexity: O(N) <--> Space Complexity: O(1) (No Extra Adjacency Matrix | Dictionary)
- Undo-Redo Button: Record the previous state to play with (Although you still be lose if clicked on mine)
- (Local) Database Recording: Save your performance to get top
- Image Hovering: Easier for viewing


# Design Pattern:
- Singleton: Guarantee that each object was run by its own & dependency state was transferred by message. There are no hidden attribute stored on other object. 

![image](https://github.com/IchiruTake/python-minesweeper/blob/main/image/%5BTest%5D%20Image%20%232.png)

- Observer: Message transferring. Interface Nodes and Core is message transmitter --- Interface is Observer

![image](https://github.com/IchiruTake/python-minesweeper/blob/main/image/%5BTest%5D%20Image%20%233.png)

![image](https://github.com/IchiruTake/python-minesweeper/blob/main/image/%5BTest%5D%20Image%20%234.png)
