# Freelancer Job Posting - Build Aegis OS

## Job Title
**Build Aegis OS Linux Distribution ISO (1-2 hours work)**

## Budget
$30 USD

## Timeline
1-2 hours of active work + 2 hours automated build time (you monitor, no intervention needed)

---

## What Needs to Be Done

Build a complete bootable Linux operating system (ISO file) from source code using Buildroot.

### Simple Steps:
1. Copy a folder to a USB stick
2. Plug USB into a Linux VM
3. Run 4 terminal commands
4. Wait for automated compilation (1-2 hours)
5. Send me the resulting ISO file

**Total active work: ~30 minutes** (rest is automated)

---

## What You'll Need

- **VirtualBox** (free) - to run the Linux VM
- **Linux VM**: Ubuntu Server 20.04 LTS (provided by you OR I can provide)
- **50GB+ disk space** on the VM
- **USB stick** (8GB+) - to transfer the code folder
- **2-3 hours total** (30 min work + 1-2 hour automated build)

---

## Detailed Instructions

### Step 1: Prepare the Code (5 minutes)
1. You provide me the AegisOS folder location or I'll send it
2. Copy `aegis-os-freemium` folder to a USB stick
3. Eject USB stick

### Step 2: Mount USB in Linux VM (5 minutes)
```bash
sudo mount /dev/sdb1 /mnt/usb
cd /mnt/usb/aegis-os-freemium
```

### Step 3: Start the Build (1 minute)
```bash
chmod +x build.sh
./build.sh
```

### Step 4: Wait for Compilation (1-2 hours)
- The script runs automatically
- You monitor progress in the terminal
- No intervention needed
- Script will finish with "Build complete" message

### Step 5: Get the ISO File (5 minutes)
1. ISO file location: `/mnt/usb/aegis-os-freemium/output/aegis-os-freemium.iso`
2. Copy to USB stick or transfer to my server
3. Verify file size: should be ~2.1GB
4. Send to me

---

## Deliverables

**MUST DELIVER:**
1. ✅ One bootable ISO file: `aegis-os-freemium.iso` (~2.1GB)
2. ✅ Proof of successful build (screenshot of "Build complete" message)
3. ✅ SHA-256 checksum verification (file integrity proof)
4. ✅ File transfer to me (via Google Drive, Dropbox, or your preferred method)

**OPTIONAL BUT NICE:**
- Note of any issues encountered and how they were resolved
- Build log file (for reference)

---

## Requirements

### Technical Requirements
- Linux (Ubuntu 20.04 LTS preferred)
- 50GB+ free disk space
- 8GB+ RAM
- 4+ CPU cores (more = faster build)
- Internet connection (to download dependencies)
- VirtualBox (free)
- USB stick (8GB+)

### Experience Required
- Comfortable with Linux terminal (basic commands)
- Can follow step-by-step instructions
- Can monitor a long-running build process
- Can transfer files

---

## Important Notes

- **Build is automated**: Once you run the script, it compiles automatically. You just monitor.
- **No coding needed**: This is not a programming job, it's a build/compilation job
- **Predictable time**: Takes exactly 1-2 hours (you know the end time upfront)
- **Simple success criteria**: If the ISO file exists and is 2.1GB, it worked
- **Low complexity**: Just follow 4 terminal commands

---

## Payment Terms

- **$30 USD** - Upon successful delivery of the ISO file and proof of build
- Escrow available (recommended for freelancer protection)

---

## How to Submit

When you apply, please confirm:
1. ✅ You have access to a Linux VM (or can set up Ubuntu Server 20.04)
2. ✅ You have 50GB+ free disk space
3. ✅ You're comfortable with Linux terminal commands
4. ✅ You can complete within 3-4 hours (including wait time)

---

## FAQ

**Q: Do I need to write code?**
A: No, this is a build job. You run existing scripts.

**Q: What if something breaks?**
A: The script handles errors. If it fails, we debug the logs together.

**Q: How do I transfer the 2.1GB file?**
A: Google Drive, Dropbox, WeTransfer, or your preferred file service.

**Q: Can you provide the Linux VM?**
A: Yes, I can provide a VirtualBox image or help you set one up.

**Q: What if the build takes longer than 2 hours?**
A: That's fine - you just wait. The $30 covers your time, not clock hours.

**Q: Do I need special knowledge?**
A: Just basic Linux terminal comfort. You're mostly copy-pasting commands.

---

## Why This Job

- Quick money ($30 for ~1 hour active work)
- Simple, predictable task
- Low technical complexity
- Clear success criteria (you know if it worked)
- Perfect for someone testing their setup or portfolio

---

**Ready to hire? Contact me with questions and I'll provide the AegisOS folder and step-by-step help.**
