def longest_common_subsequence(text1, text2):
    """
    Finds the length of the longest common subsequence between two strings.
    Time : O(nm)
    Space: O(nm)

    Args:
        text1 (str): The first string.
        text2 (str): The second string.

    Returns:
        int: The length of the longest common subsequence.
    """

    m = len(text1)
    n = len(text2)

    # Create a table to store lengths of LCS for all subproblems
    L = [[0] * (n + 1) for _ in range(m + 1)]

    # Build the table in bottom-up fashion
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif text1[i - 1] == text2[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    return L[m][n]

# Test cases
def test_longest_common_subsequence():
    assert longest_common_subsequence("abcde", "ace") == 3
    assert longest_common_subsequence("abc", "def") == 0
    assert longest_common_subsequence("bbbab", "abbbb") == 4
    assert longest_common_subsequence("abdca", "cbda") == 3

if __name__ == "__main__":
    test_longest_common_subsequence()
