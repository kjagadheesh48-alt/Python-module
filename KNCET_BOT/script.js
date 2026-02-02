let step = 0;
let userData = {};

const chat = document.getElementById("chatBody");
const input = document.getElementById("userInput");

/* BOT MESSAGE */
function bot(msg) {
  chat.innerHTML += `<p><b>Bot:</b> ${msg}</p>`;
  chat.scrollTop = chat.scrollHeight;
}

/* USER MESSAGE */
function user(msg) {
  chat.innerHTML += `<p><b>You:</b> ${msg}</p>`;
}

/* START */
bot("Welcome to KNCET College 😊 What's your name?");

/* INPUT HANDLER */
input.addEventListener("keypress", function(e) {
  if (e.key === "Enter") {
    let msg = input.value.trim();
    if (!msg) return;

    user(msg);
    input.value = "";

    if (step === 0) {
      userData.name = msg;
      bot(`Hi ${msg}! Please enter your Gmail ID`);
      step++;
    }
    else if (step === 1) {
      if (!/^\S+@gmail\.com$/.test(msg)) {
        bot("❌ Please enter a valid Gmail ID (must end with @gmail.com)");
        return;
      }
      userData.email = msg;
      bot("Enter your 10-digit Mobile Number");
      step++;
    }
    else if (step === 2) {
      if (!/^[0-9]{10}$/.test(msg)) {
        bot("❌ Please enter a valid 10-digit mobile number");
        return;
      }
      userData.mobile = msg;
      bot("Thank you ✅");
      showPurposeDropdown();
      step++;
    }
    else if (step === 3) {
      if (msg.toLowerCase() === "ug") {
        bot("UG Courses offered at KNCET 🎓:");
        bot(`
          • B.E Computer Science (CSE)<br>
          • B.E Electronics & Communication (ECE)<br>
          • B.E Electrical & Electronics (EEE)<br>
          • B.E Mechanical Engineering (MECH)<br>
          • B.E Civil Engineering (CIVIL)<br>
          • B.Tech Artificial Intelligence & Data Science (AI & DS)
        `);
        saveData();
        step++;
      }
      else if (msg.toLowerCase() === "pg") {
        bot("PG Courses offered at KNCET 🎓:");
        bot(`
          • M.E Computer Science<br>
          • M.E VLSI Design<br>
          • M.E Power Systems<br>
          • M.E Structural Engineering<br>
          • MBA
        `);
        saveData();
        step++;
      }
      else {
        bot("❌ Please type only UG or PG");
      }
    }
  }
});

/* PURPOSE DROPDOWN */
function showPurposeDropdown() {
  chat.innerHTML += `
    <p><b>Bot:</b> Please choose an option:</p>
    <select onchange="handlePurpose(this.value)">
      <option value="">-- Select --</option>
      <option value="Admissions">Admissions</option>
      <option value="Fees">Fees</option>
      <option value="Courses">Courses</option>
      <option value="Facilities">Facilities</option>
    </select>
  `;
  chat.scrollTop = chat.scrollHeight;
}

/* HANDLE PURPOSE */
function handlePurpose(value) {
  if (!value) return;

  userData.purpose = value;
  user(value);

  if (value === "Admissions" || value === "Fees") {
    bot("Admissions open for CSE, ECE, EEE, MECH, CIVIL, AI & DS.");
    bot("Please select the department:");
    showDepartmentButtons();
  } else if (value === "Courses") {
    bot("We offer UG and PG programs 📘📕");
    bot("Please type UG or PG");
    step = 3;
  } else if (value === "Facilities") {
    bot("Hostel, library, labs, transport, sports & Wi-Fi campus.");
    saveData();
  }
}

/* DEPARTMENT BUTTONS */
function showDepartmentButtons() {
  chat.innerHTML += `
    <div style="margin-top:10px;">
      <button onclick="selectDept('CSE')">CSE</button>
      <button onclick="selectDept('ECE')">ECE</button>
      <button onclick="selectDept('EEE')">EEE</button>
      <button onclick="selectDept('MECH')">MECH</button>
      <button onclick="selectDept('CIVIL')">CIVIL</button>
      <button onclick="selectDept('AI & DS')">AI & DS</button>
    </div>
  `;
  chat.scrollTop = chat.scrollHeight;
}

/* DEPARTMENT SELECT */
function selectDept(dept) {
  userData.department = dept;
  user(dept);

  const departmentInfo = {
    "CSE": { seats: 300, fees: "₹75,000" },
    "ECE": { seats: 180, fees: "₹70,000" },
    "EEE": { seats: 120, fees: "₹65,000" },
    "MECH": { seats: 150, fees: "₹60,000" },
    "CIVIL": { seats: 100, fees: "₹55,000" },
    "AI & DS": { seats: 60, fees: "₹80,000" }
  };

  const info = departmentInfo[dept];

  bot(`
    <b>${dept} Department</b><br>
    Seats Available: ${info.seats}<br>
    Counselling Fees: ${info.fees}
  `);

  userData.seats = info.seats;
  userData.fees = info.fees;

  saveData();
}

/* SAVE DATA */
function saveData() {
  let data = JSON.parse(localStorage.getItem("visitors")) || [];
  data.push({ ...userData });
  localStorage.setItem("visitors", JSON.stringify(data));
}
