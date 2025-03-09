
const getLeaderBoard = async () => {
    const response = await fetch('/api/leaderboard');
    const data = await response.json();
    return data.leaderboard;
}

export { getLeaderBoard };