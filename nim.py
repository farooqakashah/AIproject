from __future__ import annotations
import random
import sys
from time import sleep
class Nim:
    def __init__(self, initial: list = [1, 3, 5, 7]) -> None:
        # The piles are the state of the cards

        self.piles: list = initial.copy()
        # Current turn of player
        self.player: int = 0
        # Current winner
        self.winner: (None | int) = None

    @classmethod
    def available_actions(cls, piles: list) -> set:
        """
        Find the all the available actions in the provided piles.

        ## Paramenters:
        *piles:* The All piles in the game currently being played.

        ## Return:
        The set of tuples of action. In each tuple the first number is the pile number as zero indexed, and the second number displays the cards to remove from the selected pile.
        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player: int) -> int:

        """
        The function tells the which turn is next of the either player on behald of player provided.

        ## Parameters:
        *player*: The current player turn.

        ## Return:
        The int of other player's turn.
        """

        return 0 if player == 1 else 1

    def switch_player(self) -> None:

        """
        The function switches the turn from current player to other player.
        """

        self.player = Nim.other_player(self.player)

    def move(self, action: tuple) -> None:

        """
        The game make a move through this function. The piles are updated and the turn goes to next player.
            Keep track of Winner in hand to hand.

        ## Parameter:
        *action*: The action (i, j) to take in the pile.
        """

        pile, count = action

        # Update pile
        self.piles[pile] = self.piles[pile] - count
        self.switch_player()

        # Check for a winner
        for pile in self.piles:
            if pile != 0:
                return
        self.winner = self.player
        # else:
        #     self.winner = self.player
        # if all(pile == 0 for pile in self.piles):
        #     self.winner = self.player


class NimAI:
    def __init__(self, alpha: float = 0.5, epsilon: float = 0.1) -> None:
        """
        The class keeps track of the agent. This piece of code makes an AI agent
            and train that on the basis of reinforcement learning. The one
            of the attributes is the base of experience of the agent. The experience
            is based on Q values or rewards for each action taken in the current
            state either by the human or AI agent during gameplay or training of
            AI itself. The reward of 1 is awarded for the action caused in winning
            and -1 for the action in the particular state that caused in loss.
            The 0 reward which action couldn't cause win or loss and game is continued.

        ## Parameters:
        *alpha*: The learning rate, how we value the current and future reward. \n
        *epsilon*: The probability of epsilon for the exploration.

        ## Return:
        None
        """
        self.q: dict = dict()
        self.alpha: float = alpha
        self.epsilon: float = epsilon

    def update(
            self, old_state: list, action: tuple, new_state: list, reward: int
    ) -> None:

        """
        The updating of Q value for every action in the state in the game played is
            necessary for the experience of AI agent. The reward for every action in
            the state taken is stored in the dictionary of self.q with the label of
            state and action. The method to assign reward is known as Q learning Formula.
            The current rewards and the future rewards are take into consideration

        ## Parameters:
        *old_state*: The tuple of piles which were recorded before the current state. \n
        *action*: The action took on the old_state. \n
        *new_state*: The new state of piles which are formed after taking action on old_state. \n
        *reward*: The integer value for congratulations (1) or punishment (-1) or no reward (0) for the ai agent for every action by human or agent to gain experience.

        ## Return:
        None
        """

        old: float = self.get_q_value(old_state, action)
        best_future: float = self.best_future_reward(new_state)

        # Update q value according to Q learning formula
        self.q[tuple(old_state), action] = old + (
                self.alpha * ((reward + best_future) - old)
        )
        print(tuple(old_state), action, self.q[tuple(old_state), action])

    def get_q_value(self, state: list, action: tuple) -> float:
        """
        The function return the Q value for the provied action in the state of piles
            from the dictionary of self.q. If no experience found, assign the Q value 0.

        ## Paramenters:
        *state*: The state of piles. \n
        *action*: The action (i, j) to be or taken on the state.

        ## Return:
        The Q value for action in the state.
        """

        try:
            return self.q[tuple(state), action]
        except KeyError:
            return 0

    def best_future_reward(self, state: list) -> float:
        """
        The function return the max Q value of the all actions from the available
            actions in the providied state, from self.q. If no rewards found, return
            zero as Q value or reward.

        ## Parameters:
        *state*: The state of piles.

        ## Return:
        The max Q value of all actions in the provided state.
        """

        actions = list(Nim.available_actions(state))
        if not actions:
            return 0
        max_q = float("-inf")
        for action in actions:
            max_q = max(max_q, self.get_q_value(state, action))
        return max_q

    def choose_action(self, state: list, epsilon: bool = True) -> tuple[int, int]:
        """
            The function chooses action from the state for the agent. If the agent
            is training itself, then the agent chooses random action with self.epsilon
            and chooses best action with random float > self.epsilon value. The algorithm
            does exploration when training itself and choose best action when playing
            with human.

        ## Parameters:
        *state*: the list of piles. \n
        *epsilon*: When true the agent does exploration with a little exploitation.

        ## Return:
        The action based on exploitation or exploration.
        """

        # False means exploitation
        if not epsilon:
            return self.choose_best_action(state)

        # Otherwise exploration
        else:
            ran: float = random.random()
            # greedy = 1 - ran
            if ran > self.epsilon:
                return self.choose_best_action(state)
            else:
                return random.choice(list(Nim.available_actions(state)))

    def choose_best_action(self, state: list) -> tuple[int, int]:

        """
        The function chooses the action with highest Q valuefor the agent from
            available actions in the game during play or train(if required).

        ## Parameters:
        *state*: the list of piles.

        ## Return:
        The action based on exploitation or exploration.
        """
        avail_actions = list(Nim.available_actions(state))
        best_action: tuple[int, int] = random.choice(avail_actions)
        best_q: float = self.get_q_value(state, best_action)

        for action in avail_actions:
            q = self.get_q_value(state, action)
            if q > best_q:
                best_action = action
                best_q = q
        return best_action


class GamePlay:
    colors: dict = {
        "HEADER": "\033[95m",
        "OKBLUE": "\033[94m",
        "OKCYAN": "\033[96m",
        "OKGREEN": "\033[92m",
        "WARNING": "\033[93m",
        "FAIL": "\033[91m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
        "UNDERLINE": "\033[4m",
        "CBLACK": "\33[30m",
        "CWHITE": "\33[37m",
        "CYELLOW": "\33[33m",
    }

    @classmethod
    def progress_bar(cls, progress: int, total: int) -> None:
        percent = (progress / float(total)) * 100
        bar: str = "❚" * int(percent) + ("-" * (100 - int(percent)))
        print(
            f'\r{GamePlay.colors["OKBLUE"]}|{GamePlay.colors["OKGREEN"]}{bar}{GamePlay.colors["OKGREEN"]}| {GamePlay.colors["OKCYAN"]}{percent:.2f}%',
            end="\r",
        )

    @classmethod
    def train(cls, n: int) -> NimAI:

        """
        The function trains the AI agent n times and returns the trained AI agent.

        ## Parameters:
        *n*: How many times AI should be trained.

        ## Return:
        Trained AI agent.
        """

        player = NimAI()

        print("Training AI...")
        # Play n times games
        for i in range(n):
            cls.progress_bar(i + 1, n)

            game = Nim()

            # Keep the record of the current player move.
            record: dict = {0: [], 1: []}

            # Game loop
            while True:
                # Get the current state and action
                state = game.piles.copy()
                action = player.choose_action(game.piles)

                # Keep record of last state and action
                record[game.player].append((tuple(state), action))

                # Make move
                game.move(action)

                # Get the new state
                new_state = game.piles.copy()

                # When game is over, update Q values with rewards
                if not game.winner is None:
                    player.update(state, action, new_state, -1)
                    player.update(
                        record[game.player][-1][0],
                        record[game.player][-1][1],
                        new_state,
                        1,
                    )
                    break

                # If game is continued, no rewards yet
                elif len(record[game.player]):
                    player.update(
                        record[game.player][-1][0],
                        record[game.player][-1][1],
                        new_state,
                        0,
                    )

        print(GamePlay.colors["CYELLOW"], GamePlay.colors["BOLD"])
        print("Done training")
        print(f"Length of Experience Q: {len(player.q.items())}")

        # Return the trained AI
        return player

    @classmethod
    def play(cls, ai: NimAI, human: int) -> None:
        """
        Here's the gameplay where the human and agent both play against each other.
            The turn of the game is played by human or AI agent, then other until
            the one of them wins.

        ## Parameters:
        *ai*: The trained AI agent to play the game with. \n
        *human*: 0 value ndicates whether human should play first and 1 value indicates AI first turn.
        """
        # Keeping base for words against numbers
        words = [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
        ]

        # Create new game
        game = Nim()

        # Keep record of the current player move
        record: dict = {0: [], 1: []}

        # newstates
        new_states = []

        # Game loop
        while True:
            # Print contents of piles
            print()
            print("Deck of cards:")
            for i, pile in enumerate(game.piles):
                print(f"Deck number {words[i + 1]} has {pile} cards")
            print()

            # Compute available actions
            available_actions = Nim.available_actions(game.piles)

            # Let human make a move
            if game.player == human:
                print("Your Turn")
                while True:
                    try:
                        pile = int(input("Choose Deck: "))
                        pile -= 1
                        count = int(input("Choose Count: "))
                    except ValueError:
                        print("Kindly enter int value.")
                    else:
                        if (pile, count) in available_actions:
                            break
                        else:
                            print("Invalid move, try again.")

            # Have AI choose action
            else:
                print("AI's Turn")
                pile, count = ai.choose_action(game.piles, epsilon=False)
                print(f"AI chose to take {count} cards from Deck {words[pile + 1]}.")

            # Get the current state and action
            state = game.piles.copy()
            action = (pile, count)

            # Update the record with move
            record[game.player].append((tuple(state), action))

            # Make move
            game.move(action)

            # Get the new state
            new_state = game.piles.copy()
            new_states.append(new_state)

            # Check for winner
            if game.winner is not None:
                print()
                print("GAME IS OVER")
                winner = "Human" if game.winner == human else "AI"
                print(f"Winner is {winner}")
                return



def main(loops: int = 10000) -> None:
    ai = GamePlay.train(loops)
    print()
    print(
        "The game consists of four decks having several cards. You have to remove several cards upon your turn\n"
        "in any order, such that the player having last turn will lose the game."
    )
    sleep(1)
    print()
    while True:
        while True:
            try:
                turn = int(input("Do you want your turn or AI Turn? Yours: 0, AI: 1: "))
            except ValueError:
                print("Kindly enter int value")
            else:
                if turn == 0 or turn == 1:
                    break
        GamePlay.play(ai, turn)
        if input("Do you want to Exit? [y]: ").lower() == "y":
            sys.exit(0)


# Calling main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\b\bYou are exit now....")
