# Modding the AAMI Crunching Game
The AAMI Crunching Game is a highly moddable game. Being open-source, anything about the game can be modified. From new status effects and hats, to entirely new entities.
## Status Effects
To add new status effects, start by adding a PNG image to represent the falling hat in `assets/hats/<name>/png`. Then add the `<name>` (without the `.png`) as a python string literal to `hatByRank`
`src/effect.py` and make a class inheriting `effect.Effect` to define the status effect that is gained when the hat is caught and put your effect constructor in the dictionary
`effectByHat` with the key being your hat's `<name>` (again without the `.png` extension). The `.png` extension of the image file name MUST be lower-case. 

***THIS MODDING API IS SUBJECT TO CHANGE IN THE NEAR FUTURE***
