const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const twilio = require('twilio');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Twilio credentials (replace with your own)
const accountSid = "ACdd9aeeeea13710ecec82000f2c76ca71";
const authToken  = "8WJKRWKWEJ6JPQ1ABUUL8FSV";
const serviceSid = '8WJKRWKWEJ6JPQ1ABUUL8FSV'; // For OTP / Verify service
const client = twilio(accountSid, authToken);

// Store OTPs temporarily (for demo, use database in production)
const otpStore = {};

// Send OTP
app.post('/send-otp', async (req, res) => {
  const { mobile } = req.body;
  if (!mobile) return res.json({ success: false, message: "Mobile number missing" });

  try {
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    otpStore[mobile] = otp; // store OTP temporarily

    // For real SMS, uncomment below (requires Twilio verified number)
    // await client.messages.create({
    //   body: `Your OTP is ${otp}`,
    //   from: '+1XXXXXXXXXX', // your Twilio number
    //   to: '+91' + mobile
    // });

    console.log(`OTP for ${mobile} is ${otp}`); // For testing
    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.json({ success: false });
  }
});

// Verify OTP
app.post('/verify-otp', (req, res) => {
  const { mobile, otp } = req.body;
  if (otpStore[mobile] && otpStore[mobile] === otp) {
    delete otpStore[mobile]; // remove after success
    return res.json({ success: true });
  }
  res.json({ success: false });
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
