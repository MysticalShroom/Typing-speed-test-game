# **WPM Typing Test \- Project Report**

## **1\. Introduction**

I made the WPM Typing Test so you can quickly check how fast and accurately you type right in the terminal.

### **1a. What is your application?**

The WPM Typing Test is a program made in Python that runs in the terminal. It lets users see how fast and accurate they can type. The main goal is to give users a simple way to see their typing speed in Words Per Minute (WPM).

Key features:

* **Terminal UI:** Uses the curses library to show the test directly in the terminal window.  
* **Difficulty Levels:** Users can pick a difficulty: easy (short words), medium, hard (long words), or Random (mix of all word lengths).  
* **Word Count:** Users can choose how many words (5-50) they want in the test.  
* **Word Source:** Gets random words from an online API. If the API doesn't work, it uses a built-in backup list of words.  
* **Live Feedback:** While typing:  
  * Correct letters are green.  
  * Incorrect letters are red.  
  * The top of the screen shows the time passed, error count, and current WPM speed.  
* **Final Results:** After typing the last word, the program shows:  
  * Final WPM score.  
  * Accuracy percentage.  
  * Total errors.  
  * Total time taken.  
* **Saving Results:** Saves the results of every finished test (time, difficulty, count, WPM, accuracy, errors, duration) into the typing\_results.txt file.  
* **Options After Test:** The user can choose to:  
  * Retry the same test again.  
  * Start a completely new test (choose difficulty and word count again).  
  * Quit the program.

### **1b. How to run the program?**

To set up and run the program:

1. **Need:** Python 3 installed. Git (optional, for cloning).  
2. **Get Code:** Download or clone the project files into a folder (e.g., WPMTest).  
3. **Go to Folder:** Open your terminal and go into the project folder:  
   cd path/to/your/WPMTest

4. **Create Virtual Environment:**  
   python \-m venv .venv

5. **Activate Virtual Environment:**  
   * Windows: .\\.venv\\Scripts\\activate  
   * macOS/Linux: source .venv/bin/activate  
     You should see (.venv) in your prompt.  
6. **Install Required Packages:**  
   \# For Windows (curses \+ API access)  
   pip install windows-curses requests

   \# For macOS/Linux (API access)  
   \# pip install requests

7. **Run:**  
   python main.py

   The test should start in the terminal.

### **1c. How to use the program?**

Once running (python main.py):

1. **Choose Difficulty:** Press 1, 2, 3, or 4 for Easy, Medium, Hard, or Random accordingly. Press ESC to quit.  
2. **Choose Word Count:** Type a number (5-50) and press Enter. Backspace works for changing the numbers. Press ESC to quit.  
3. **Start:** Press any key when ready.  
4. **Type:** The words appear. Type them. The timer starts when an input is detected. Green means correct, red means error. Use Backspace to fix errors. The stats at the top update live.  
5. **Results:** When done, you'll see your final WPM, Accuracy %, Errors, and Time. Below that, you'll see options.  
6. **Next Step:** Press R to retry the same words. Press N to start a new test. Press any other key to quit.  
7. **History:** Open typing\_results.txt in the project folder to see past results.

## **2\. Body / Analysis**

This section explains how the program was made, covering the main features, how OOP ideas were used, and the design pattern chosen.

### **2a. Functional Requirements Implementation**

How the program does its job:

* **Getting User Choices:** The TypingTest class shows menus for picking difficulty (\_show\_difficulty\_screen) and word count (\_show\_word\_count\_screen). It uses curses to display text and get key presses. It also makes sure the word count is valid (5-50).  
  \# Getting difficulty choice  
  key \= self.stdscr.getkey()  
  if key in ("1", "2", "3", "4"): return ...

* **Getting Text:** The ApiWordLoader class (in text\_loader.py) gets words. It tries an online API first. If that fails, it uses a backup list. TypingTest uses this loader object to get the text for the test.  
  \# Getting text in TypingTest.start  
  self.target\_text \= self.text\_loader.load()

* **Showing the Test UI:** The \_run\_test runs the typing part. \_display\_test\_ui draws the screen using curses. It shows info at the top (like time, errors, WPM) and the words. Typed letters are green if right, red if wrong.  
  \# Inside \_display\_test\_ui loop, setting color  
  color\_pair\_num \= 1 if typed\_char \== target\_char else 2 \# Green or Red  
  self.stdscr.addstr(..., curses.color\_pair(color\_pair\_num))

* **Handling Typing Input:** \_run\_test reads keys the user presses (stdscr.getch()). It checks if it's a letter, Backspace, or ESC. Letters are stored. If a letter is wrong, the error count goes up. Backspace removes the last letter and lowers the error count if the deleted letter was wrong.  
  \# Inside \_run\_test loop, handling backspace  
  if key\_code in BACKSPACE\_CODES:  
      if self.current\_text:  
          \# ... logic to pop and maybe fix error count ...

* **Calculating WPM and Accuracy:** Separate functions in utils.py do the math. calculate\_wpm runs during the test. calculate\_accuracy runs after the test.  
  \# Calling the calculation functions  
  self.wpm \= calculate\_wpm(len(self.current\_text), time\_elapsed)  
  accuracy \= calculate\_accuracy(target\_len, self.errors)

* **Showing Results and Options:** After typing, \_prompt\_retry shows the final scores and asks the user to press 'R', 'N', or another key.  
* **Saving Results:** The \_save\_results\_to\_file method adds a line with the test results to the typing\_results.txt file.  
  \# Inside \_save\_results\_to\_file  
  with open(RESULTS\_FILENAME, "a", encoding="utf-8") as f:  
      f.write(result\_line \+ "\\n")

### **2b. Object-Oriented Programming (OOP) Principles**

The program uses four main OOP ideas:

* **Encapsulation:** Keeping data and functions together in classes. TypingTest holds test information (words, errors, time) and methods to run the test. ApiWordLoader holds the word list and code to get words. Methods starting with \_ are mostly for internal class use.  
* **Abstraction:** Hiding complex details. TextLoader is a simple plan (an Abstract Base Class) that just requires a load() method. TypingTest uses this plan without knowing how ApiWordLoader actually gets the words (API or backup).  
  \# text\_loader.py \- The simple plan  
  class TextLoader(ABC):  
      @abstractmethod  
      def load(self) \-\> str: pass

* **Inheritance:** Creating a new class based on another. ApiWordLoader inherits from TextLoader. It follows the TextLoader plan by providing the actual code for the load() method.  
  \# text\_loader.py \- Following the plan  
  class ApiWordLoader(TextLoader):  
      def load(self) \-\> str:  
          \# ... code to provide words ...

* **Polymorphism:** Using different objects in the same way. TypingTest calls self.text\_loader.load(). This works the same way whether self.text\_loader is an ApiWordLoader or a different kind of loader, because they both follow the TextLoader plan.

### **2c. Design Pattern Used: Strategy**

The program uses the **Strategy Pattern**.

* **The Idea:** Have different ways (strategies) to do something (like loading words). Put each way in its own class. Let the main program choose which strategy to use.  
* **How it's used:**  
  * Strategies: Getting words from the API, or using a backup list.  
  * Interface: TextLoader defines the common load() method.  
  * Concrete Strategy: ApiWordLoader provides the API/fallback way to load().  
  * Context: TypingTest uses the TextLoader object to get words via load().  
* **Why it's good:** Makes it easy to change how words are loaded without changing TypingTest.

### **2d. Composition Principle**

The program uses **Composition** ("has-a" relationship).

* **How it's used:** The TypingTest class *has-a* TextLoader object inside it (self.text\_loader).  
* **Benefit:** TypingTest uses the TextLoader object to do the job of loading words. This keeps the code organized: TypingTest handles the test, TextLoader handles getting words.

## **3\. Results and Conclusions**

### **3a. Result**

* The project successfully created a working typing test program that runs in the terminal.  
* It successfully measures typing speed (WPM) and accuracy, providing live feedback to the user.  
* A main challenge was dealing with unreliable online APIs for word lists; adding a backup word list fixed this problem when the API failed.  
* Setting up the programming environment, especially getting curses to work on Windows and making sure the virtual environment was set up right, took some extra time.  
* AI was used in troublesome cases (unit tests, loader switch, UI fixes and the report)

### **3b. Conclusions and Future Prospects**

* **What was achieved?** This project successfully made a working typing test game/program that runs in the terminal. It was good practice using Python, OOP ideas, reading from file & saving to file, using an API.  
* **What is the result?** The result is a program that people can use to practice typing. It lets users pick a difficulty and word count, shows feedback as they type, and saves their scores.  
* **What could be added later?** The program could be improved later. It could track high scores or have user logins. Users could be allowed to type their own text instead of random words. The display could be better at handling different window sizes. More ways to get words could be added (like from a database). Settings could also be put in a separate file.