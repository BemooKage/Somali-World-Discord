"""Word manager using Trie structure"""
import random
from typing import List
from game.trie import Trie


class WordleManager:
    """Wordle Manager"""

    def __init__(self):
        self.trie = Trie()

    def get_random_word(self):
        """Gets random word from Trie structure"""
        nodes = list(self.trie.root.values())
        count = 5
        output = ""
        while count > 0:
            val = random.sample(population=nodes, k=1)[0]
            output += val.value
            nodes = list(val.children.values())

            count -= 1
        return output


    def is_valid_word(self, word: str) -> bool:
        """Checks if word in true"""
        return self.trie.is_valid(word=word)
    
    def autocomplete(self, prefix: str) -> List[str]:
        """Autocomplete from given prefix through trie"""
        return self.trie.search(prefix)


