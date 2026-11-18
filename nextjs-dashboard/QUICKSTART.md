# ⚡ Quick Start Guide

Get the dashboard running in 2 minutes!

## 1️⃣ Install Dependencies

```bash
cd nextjs-dashboard
npm install
```

**Windows PowerShell:**
```powershell
cd .\nextjs-dashboard\
npm install
```

**Expected time**: 2-3 minutes (first time only)

## 2️⃣ Run Development Server

```bash
npm run dev
```

**Output:**
```
> next dev

▲ Next.js 14.0.0
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 2.1s
```

## 3️⃣ Open in Browser

Visit: **http://localhost:3000**

✨ You should see the beautiful quantum research dashboard!

## 📊 What You'll See

### Top Section
- Navigation bar with smooth scroll
- Hero heading with gradient text
- Project title and description

### Section 1: Problem & Objective
- Research question clearly stated
- Motivation cards
- Why this matters

### Section 2: Quantum Formulation
- Amplitude encoding formula explained
- Qubit requirement table
- **INTERACTIVE**: 3D rotating quantum circuit visualization

### Section 3: Methodology
- Implementation stack
- 22 modules overview
- **INTERACTIVE**: 3D rotating image reconstruction

### Section 4: Experiments
- 6 experiment cards (A-F)
- Evaluation metrics explanation
- Full experimental design

### Section 5: Results & Analysis
- **Tab Navigation**: Switch between views
- 4 Interactive charts:
  - Resolution Scaling
  - Shot Count Impact
  - Noise Sensitivity
  - Quantum vs Classical Comparison

### Section 6: Limitations
- No quantum advantage (currently)
- Future potential
- Research integrity

## 🎮 Interactive Features

### 3D Scenes
- **Quantum Circuit**: Click and drag to rotate, scroll to zoom
- **Image Reconstruction**: Auto-rotates, click to interact

### Charts
- **Hover**: See exact values
- **Tabs**: Switch between different analyses
- **Smooth animations**: Data updates smoothly

### Tables
- **Sortable columns**: Click header to sort
- **Hover effects**: Rows highlight on hover
- **Responsive**: Works on mobile too

## 🛠️ Customization

### Change Colors
Edit `tailwind.config.js`:

```javascript
colors: {
  'quantum-primary': '#667eea',    // Change this color
  'quantum-accent': '#f093fb',     // Or this one
}
```

Then restart: `Ctrl+C` and `npm run dev`

### Edit Content
Edit `src/app/page.tsx` to change:
- Text content
- Chart data
- Experiment descriptions
- Conclusions

### Modify 3D Scenes
Edit `src/components/QuantumCircuit3D.tsx` or `ImageReconstruction3D.tsx`:
- Add more qubits
- Change gate types
- Adjust colors
- Modify rotation speed

## 🚀 Build for Production

```bash
npm run build
npm start
```

This creates an optimized version for presentation/deployment.

## 📱 Mobile View

The dashboard is fully responsive:
- Tap navigation to toggle menu
- Swipe to interact with 3D scenes
- All charts adapt to screen size
- Touch-friendly buttons and controls

## 🆘 Troubleshooting

### "Cannot find module" error
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npm run dev
```

### 3D scenes not showing
- [ ] Check if WebGL is enabled (Chrome → Settings → Advanced → System → Hardware acceleration)
- [ ] Try a different browser (Chrome, Firefox, Edge)
- [ ] Update graphics drivers
- [ ] Check browser console for errors (F12)

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

Then visit: http://localhost:3001

### Slow performance
- Close other browser tabs
- Disable browser extensions
- Try incognito/private mode
- Reduce animation complexity

## 📚 File Structure

```
nextjs-dashboard/
├── src/
│   ├── app/
│   │   ├── page.tsx              ← Main dashboard
│   │   ├── layout.tsx            ← Root layout
│   │   └── globals.css           ← Styles
│   └── components/
│       ├── Navbar.tsx
│       ├── QuantumCircuit3D.tsx   ← 3D circuit
│       ├── ImageReconstruction3D.tsx  ← 3D image
│       ├── Charts.tsx             ← All charts
│       └── ...
├── public/                        ← Static files
├── package.json
├── tailwind.config.js             ← Colors, fonts
├── tsconfig.json
└── README.md
```

## 🎯 For Presentation

### Before Presentation
```bash
# Build optimized version
npm run build

# Test production build
npm start

# Visit http://localhost:3000
# Try all interactions, charts, 3D scenes
```

### During Presentation
- Keep only dashboard and one terminal visible
- Have backup laptop with full project
- Have USB with screenshots as fallback
- Test audio if presenting remotely
- Have PDF of slides as backup (unlikely to need)

### After Presentation
You can:
- Deploy to Vercel: `vercel`
- Share with link: `vercel.com/your-username/quantum-research`
- Keep running locally for demos
- Push to GitHub: `git push`

## 💻 Commands Reference

```bash
# Install (first time)
npm install

# Development (with hot reload)
npm run dev

# Production build
npm run build

# Run production version
npm start

# Check for issues
npm run lint
```

## 🎓 Learning Resources

If you want to customize further:

- **Next.js**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Three.js**: https://threejs.org/docs
- **Framer Motion**: https://www.framer.com/motion
- **Recharts**: https://recharts.org

## ✅ Ready to Go!

You now have:
- ⚛️ 3D Quantum Circuit Visualization
- 📊 Interactive Charts
- 🎨 Modern UI/UX
- 📱 Responsive Design
- ✨ Smooth Animations
- 🚀 Production Ready

**Everything ready for your mid-term evaluation! 🎉**

---

## 🔗 Quick Links

- **Main Dashboard**: http://localhost:3000
- **Next.js Docs**: https://nextjs.org
- **GitHub**: Your repository
- **Presentation Guide**: See `PRESENTATION_GUIDE.md`
- **Full README**: See `README.md`

---

**Questions?** Check README.md for more details or PRESENTATION_GUIDE.md for presentation tips.

Good luck! 🚀
