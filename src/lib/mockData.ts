export const stats = {
  totalConversations: 12847,
  openTickets: 38,
  aiResolved: 9421,
  humanHandover: 312,
  avgResponseTime: "1m 24s",
  resolutionRate: 87,
};

export const sentimentData = [
  { day: "Sat", positive: 240, neutral: 120, negative: 30 },
  { day: "Sun", positive: 280, neutral: 140, negative: 28 },
  { day: "Mon", positive: 320, neutral: 160, negative: 45 },
  { day: "Tue", positive: 360, neutral: 150, negative: 38 },
  { day: "Wed", positive: 410, neutral: 170, negative: 42 },
  { day: "Thu", positive: 380, neutral: 180, negative: 36 },
  { day: "Fri", positive: 450, neutral: 190, negative: 30 },
];

export const channelData = [
  { name: "Messenger", value: 5420, color: "hsl(220 90% 60%)" },
  { name: "WhatsApp", value: 3890, color: "hsl(145 65% 45%)" },
  { name: "Website", value: 2110, color: "hsl(250 84% 60%)" },
  { name: "Instagram", value: 1427, color: "hsl(320 75% 60%)" },
];

export const conversations = [
  { id: "1", name: "Rahim Ahmed", channel: "Messenger", message: "ভাই, এই শাড়িটা কি স্টকে আছে?", time: "2m", unread: 2, sentiment: "positive", avatar: "RA" },
  { id: "2", name: "Fatima Khan", channel: "WhatsApp", message: "Order #4521 delivery status?", time: "8m", unread: 0, sentiment: "neutral", avatar: "FK" },
  { id: "3", name: "Karim Hossain", channel: "Website", message: "ডেলিভারি চার্জ কত ঢাকার বাইরে?", time: "15m", unread: 1, sentiment: "neutral", avatar: "KH" },
  { id: "4", name: "Nusrat Jahan", channel: "Messenger", message: "আমার অর্ডার এখনো আসেনি!", time: "32m", unread: 3, sentiment: "negative", avatar: "NJ" },
  { id: "5", name: "Tanvir Islam", channel: "WhatsApp", message: "Thanks! Got the product 👍", time: "1h", unread: 0, sentiment: "positive", avatar: "TI" },
  { id: "6", name: "Sadia Rahman", channel: "Instagram", message: "Price please?", time: "2h", unread: 0, sentiment: "neutral", avatar: "SR" },
  { id: "7", name: "Mehedi Hasan", channel: "Messenger", message: "ভাই কোচিং ক্লাস কখন শুরু?", time: "3h", unread: 1, sentiment: "positive", avatar: "MH" },
];

export const tickets = {
  open: [
    { id: "T-1024", title: "Refund for damaged product", customer: "Nusrat Jahan", priority: "high", sentiment: "negative", agent: "Ayesha" },
    { id: "T-1025", title: "Product size inquiry", customer: "Karim Hossain", priority: "medium", sentiment: "neutral", agent: "AI" },
  ],
  pending: [
    { id: "T-1019", title: "Bulk order discount request", customer: "Tanvir Islam", priority: "medium", sentiment: "positive", agent: "Rifat" },
    { id: "T-1020", title: "Delivery delay complaint", customer: "Sadia Rahman", priority: "high", sentiment: "negative", agent: "Ayesha" },
    { id: "T-1021", title: "Class schedule question", customer: "Mehedi Hasan", priority: "low", sentiment: "neutral", agent: "AI" },
  ],
  resolved: [
    { id: "T-1015", title: "Payment confirmation", customer: "Fatima Khan", priority: "low", sentiment: "positive", agent: "AI" },
    { id: "T-1016", title: "Address update", customer: "Rahim Ahmed", priority: "low", sentiment: "neutral", agent: "AI" },
  ],
  closed: [
    { id: "T-1010", title: "Wrong item received", customer: "Sumi Akter", priority: "high", sentiment: "negative", agent: "Rifat" },
  ],
};

export const faqs = [
  { id: 1, question: "ডেলিভারি চার্জ কত?", answer: "ঢাকার ভিতরে ৬০ টাকা, ঢাকার বাইরে ১২০ টাকা।", category: "Delivery", language: "Bangla" },
  { id: 2, question: "What is your return policy?", answer: "We accept returns within 7 days of delivery for unused products.", category: "Returns", language: "English" },
  { id: 3, question: "How to track my order?", answer: "Use the tracking link sent via SMS after dispatch.", category: "Orders", language: "English" },
  { id: 4, question: "পেমেন্ট অপশন কি কি?", answer: "bKash, Nagad, Rocket, Card এবং Cash on Delivery।", category: "Payment", language: "Bangla" },
  { id: 5, question: "ক্লাসের সময়সূচি কেমন?", answer: "সকাল ৯টা থেকে রাত ৯টা পর্যন্ত ব্যাচ আছে।", category: "Schedule", language: "Bangla" },
];

export const products = [
  { id: 1, name: "Cotton Saree - Premium", price: 2400, stock: "in_stock", desc: "100% cotton, handwoven Tangail saree", policy: "7 days return" },
  { id: 2, name: "Punjabi - Eid Special", price: 1850, stock: "low", desc: "Embroidered cotton punjabi, all sizes", policy: "5 days return" },
  { id: 3, name: "Three-Piece Set", price: 3200, stock: "in_stock", desc: "Unstitched georgette three-piece", policy: "7 days return" },
  { id: 4, name: "Kids T-shirt Pack", price: 950, stock: "out", desc: "Pack of 3, ages 4-10", policy: "No return" },
  { id: 5, name: "Hijab Collection", price: 450, stock: "in_stock", desc: "Premium chiffon hijab", policy: "Exchange only" },
];

export const messages = [
  { from: "customer", text: "ভাই, এই শাড়িটা কি স্টকে আছে?", time: "10:24 AM" },
  { from: "ai", text: "জ্বি, Cotton Saree - Premium টি স্টকে আছে। দাম ২৪০০ টাকা। কোন রঙ চান?", time: "10:24 AM" },
  { from: "customer", text: "লাল আছে?", time: "10:25 AM" },
  { from: "ai", text: "জ্বি লাল, নীল, সবুজ এবং কালো রঙে available আছে। অর্ডার করতে চান?", time: "10:25 AM" },
  { from: "customer", text: "হ্যাঁ, ডেলিভারি চার্জ কত?", time: "10:26 AM" },
];
