// Practice Questions (text only)
const practiceQuestions = {
  coding: [
    "Write a function to reverse a string.",
    "Explain difference between let, var, and const in JavaScript.",
    "Find factorial of a number using recursion.",
    "What is Big O notation? Explain with example.",
    "Implement binary search algorithm.",
    "Write a program to check if a number is prime.",
    "Explain difference between synchronous and asynchronous programming.",
    "What is event bubbling in JavaScript?",
    "How does garbage collection work in Java?",
    "Write SQL query to find second highest salary in a table."
  ],
  aptitude: [
    "If A = 40% of B and B = 20% of C, what is A in terms of C?",
    "The average of 5 consecutive numbers is 20. Find the largest.",
    "Train of 100m passes a pole in 10s. Find speed.",
    "Simplify: (25% of 200) + (30% of 150).",
    "What is compound interest on 5000 for 2 years at 10%?",
    "If 3 workers complete a task in 6 days, how long will 6 workers take?",
    "Find the probability of getting a head when tossing a fair coin.",
    "A car travels 60km in 90 minutes. Find speed in km/h.",
    "If 2x + 3 = 11, find x.",
    "A person bought an article for 500 and sold it for 650. Find profit%."
  ],
  reasoning: [
    "If CAT = 3120, then DOG = ?",
    "Find the odd one: Mango, Apple, Potato, Banana.",
    "All squares are rectangles. All rectangles are polygons. Are all squares polygons?",
    "Pointing to a lady, a man said, ‘She is my mother’s only son’s wife’. How is the lady related to the man?",
    "Series: 2, 6, 12, 20, ?",
    "If TOMORROW is coded as QNLNPPQT, then TODAY is coded as?",
    "Find missing number: 7, 14, 28, ?, 112",
    "If in a code CAT = DBU, then DOG = ?",
    "Statement: All engineers are professionals. Conclusion: All professionals are engineers. (True/False?)",
    "Which one does not belong: Pen, Pencil, Eraser, Book?"
  ],
  interview: [
    "Tell me about yourself.",
    "Why should we hire you?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in 5 years?",
    "Explain a challenge you faced and how you solved it.",
    "Describe a time you worked in a team.",
    "What do you know about our company?",
    "How do you handle stress and pressure?",
    "What is your biggest achievement so far?",
    "Why are you interested in this role?"
  ]
};

// Quiz Questions (with options + answer)
const quizQuestions = {
  coding: [
    { q: "Which language is primarily used for styling web pages?", options: ["HTML", "CSS", "Python"], answer: "CSS" },
    { q: "What does JS stand for?", options: ["Java Style", "JavaScript", "Just Script"], answer: "JavaScript" },
    { q: "Which data structure works on FIFO?", options: ["Stack", "Queue", "Tree"], answer: "Queue" },
    { q: "Which keyword is used to create a class in Python?", options: ["def", "class", "object"], answer: "class" },
    { q: "Which is not a programming language?", options: ["Java", "C++", "HTML"], answer: "HTML" },
    { q: "Which symbol is used for comments in Python?", options: ["//", "#", "/* */"], answer: "#" },
    { q: "Which HTML tag is used to create a hyperlink?", options: ["<a>", "<link>", "<href>"], answer: "<a>" },
    { q: "Which algorithm is used for shortest path?", options: ["Dijkstra", "Binary Search", "Merge Sort"], answer: "Dijkstra" }
  ],
  aptitude: [
    { q: "What is 15 + 35?", options: ["40", "45", "50"], answer: "50" },
    { q: "If 20% of X = 40, find X.", options: ["100", "150", "200"], answer: "200" },
    { q: "The ratio 2:3 is equivalent to?", options: ["6:9", "4:5", "8:12"], answer: "6:9" },
    { q: "Simplify: (12 × 8) ÷ 6", options: ["14", "16", "18"], answer: "16" },
    { q: "What is the average of 10, 20, 30, 40?", options: ["20", "25", "30"], answer: "25" },
    { q: "If simple interest on 2000 in 2 years is 400, rate% is?", options: ["5%", "10%", "20%"], answer: "10%" },
    { q: "A man walks 2 km north, then 3 km east. Distance from start?", options: ["3 km", "5 km", "6 km"], answer: "√13 km (~3.6 km)" }
  ],
  reasoning: [
    { q: "Which is odd one out?", options: ["Circle", "Triangle", "Rectangle"], answer: "Circle" },
    { q: "If A = 1, B = 2, Z = ?", options: ["25", "26", "27"], answer: "26" },
    { q: "All men are mortal. Socrates is a man. So Socrates is?", options: ["Immortal", "Mortal", "Unknown"], answer: "Mortal" },
    { q: "Next in series: 2, 4, 8, 16, ?", options: ["24", "32", "64"], answer: "32" },
    { q: "Odd one: Dog, Cat, Cow, Sun", options: ["Dog", "Cat", "Sun"], answer: "Sun" },
    { q: "If BLUE = 2134, then GREEN = ?", options: ["71553", "14253", "34521"], answer: "71553" },
    { q: "Find missing number: 3, 6, 12, 24, ?", options: ["36", "48", "50"], answer: "48" }
  ],
  interview: [
    { q: "Best way to answer 'Tell me about yourself'?", options: ["Talk about childhood", "Summarize career + skills", "Talk about hobbies only"], answer: "Summarize career + skills" },
    { q: "What should you avoid in interviews?", options: ["Confidence", "Eye contact", "Lying"], answer: "Lying" },
    { q: "If asked about weakness, you should?", options: ["Say you have none", "Share a minor weakness with improvement", "List all weaknesses"], answer: "Share a minor weakness with improvement" },
    { q: "When interviewer asks 'Any questions?', best response is?", options: ["No, thank you", "Ask about role growth", "Ask about salary immediately"], answer: "Ask about role growth" },
    { q: "In HR rounds, main focus is?", options: ["Technical depth", "Communication & personality", "Coding speed"], answer: "Communication & personality" },
    { q: "Which is best way to handle a technical question you don’t know?", options: ["Guess randomly", "Admit and show learning approach", "Stay silent"], answer: "Admit and show learning approach" },
    { q: "What should you research before an interview?", options: ["Company background", "Weather forecast", "Sports scores"], answer: "Company background" }
  ]
};
