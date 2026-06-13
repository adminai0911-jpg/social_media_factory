import os
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - AUTOPILOT - %(levelname)s - %(message)s")
logger = logging.getLogger("Autopilot")

def run_bot(interval_minutes=60):
    logger.info("🚀 STARTING THE MAGIC AUTOPILOT V5...")
    
    orchestrator_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "orchestrator"))
    vault_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "output_vault"))
    os.makedirs(vault_dir, exist_ok=True)
    
    generation = 1
    
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"--- STARTING GENERATION #{generation} ---")
        
        try:
            # 1. Run the V5 Generator
            subprocess.run(["python", "generate.py"], cwd=orchestrator_dir, check=True)
            
            # 2. Move output to Vault
            source_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "final_reel_v5.mp4"))
            dest_file = os.path.join(vault_dir, f"viral_masterpiece_{timestamp}.mp4")
            
            if os.path.exists(source_file):
                os.rename(source_file, dest_file)
                logger.info(f"✅ Masterpiece #{generation} saved to: {dest_file}")
                
                # 3. Auto-Upload to Socials
                try:
                    from uploader import upload_to_facebook_reels
                    # We upload the local file to FB
                    upload_to_facebook_reels(dest_file, "This fact will mess with your head... 🤯🧠 #psychology #wealth #mindset")
                except Exception as e:
                    logger.error(f"Upload failed: {e}")
                
            else:
                logger.error("❌ Output file not found. Engine failed.")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Generation #{generation} failed: {e}")
            
        logger.info(f"💤 Sleeping for {interval_minutes} minutes before the next generation...\n")
        time.sleep(interval_minutes * 60)
        generation += 1

if __name__ == "__main__":
    # Runs forever, generating 1 video every 60 minutes
    run_bot(interval_minutes=60)
