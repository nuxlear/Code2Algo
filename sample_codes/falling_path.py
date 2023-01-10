class Solution:
    def minFallingPathSum(self, matrix: List[List[int]]) -> int:
        dp = [[None for col in row] for row in matrix]

        min_sum = None
        for i in range(len(matrix)):
            s = self.get_DP_value(matrix, dp, 0, i)
            if min_sum is None or min_sum > s:
                min_sum = s

        return min_sum

    def get_DP_value(self, matrix, dp, r, c):
        N = len(matrix)

        if c < 0 or c >= N:
            return None
        if r >= N:
            return 0

        if dp[r][c] is not None:
            return dp[r][c]

        paths = [
            self.get_DP_value(matrix, dp, r + 1, c - 1),
            self.get_DP_value(matrix, dp, r + 1, c),
            self.get_DP_value(matrix, dp, r + 1, c + 1),
        ]
        val = matrix[r][c] + min([x for x in paths if x is not None])
        dp[r][c] = val
        return val