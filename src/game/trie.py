"""Easier Trie Structure"""

import csv
import os
from typing import Dict, List, Optional


class TrieNode:
    """Trie Node"""

    def __init__(self, current_value: str):
        self.value = current_value
        self.is_final = False
        self.children: Dict[str, TrieNode] = {}

    def __str__(self) -> str:
        return f"{self.value} -> [{[child for child in self.children]}]"

    def __eq__(self, value: object) -> bool:
        return value == self.value


class Trie:
    """Trie Data structure for querying and search"""

    def __init__(self):
        self.root = {}
        self.size = 0
        self._setup()

    def add_word(self, word: str):
        """adds full word"""
        word = word.lower()
        if word[0] not in self.root:
            new_node = TrieNode(word[0])
            self.root[word[0]] = new_node
            return self._add_word(word[1:], node=new_node)

        return self._add_word(word[1:], node=self.root[word[0]])

    def _add_word(self, word: str, node: TrieNode):
        """private add word"""
        if not word:
            return None

        if word[0] not in node.children:
            new_node = TrieNode(word[0])
            if not word[1:]:
                new_node.is_final = True
            node.children[word[0]] = new_node
            self.size += 1
            return self._add_word(word[1:], node=new_node)
        else:
            return self._add_word(word[1:], node=node.children[word[0]])

    def is_valid(self, word: str) -> bool:
        """Searches Trie if word exists"""
        for letter in word:
            if letter in self.root:
                return self._is_valid(word=word[1:], node=self.root[letter])
        return False

    def _is_valid(self, word: str, node: Optional[TrieNode]):
        if not word and node.is_final == True:
            return True
        elif not node:
            return False

        if word[0] in node.children:
            return self._is_valid(word=word[1:], node=node.children[word[0]])
        return False

    def find_from(self, prefix: str, node: TrieNode) -> List[str]:
        """Returns all valid words from given prefix"""
        def dfs(current_node: TrieNode, current_word: str, results: List[str]):
            if current_node.is_final:
                results.append(current_word)

            for char, child_node in current_node.children.items():
                dfs(child_node, current_word + char, results)

        # Find the node corresponding to the last character of the word
        current_node = node
        for char in prefix:
            if char not in current_node.children:
                return []  # No words with this prefix
            current_node = current_node.children[char]

        # Perform DFS from this node to find all completions
        completions = []
        dfs(current_node, prefix, completions)
        return completions

    def search(self, prefix: str) -> List[str]:
        """Searches all valid words from current prefix"""
        head_letters = TrieNode(current_value="")
        head_letters.children = self.root
        return self.find_from(prefix, head_letters)

    def _setup(self):
        """Set up Trie using wordlist"""
        with open("./src/data/somali_ngrams.csv", mode="r", encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header
            for row in csv_reader:
                word, count = row
                count = int(count)
                if not word.isalpha():
                    continue
                if len(word) == 5 and count > 500:
                    self.add_word(word=word)
                if self.size > 500:
                    break
            file.close()
        print(f"Total size: {self.size}")

    def _setup2(self):
        """setup words from txt"""
        with open("./src/data/somali.txt", mode="r", encoding="utf-8") as file:
            lines = file.readlines()
            for word in lines:
                word = word.strip().lower()
                if word.isalpha() and len(word) == 5:
                    self.add_word(word=word)

                if self.size > 200:
                    break
            file.close()
        print(f"Total size is: {self.size}")
