"""
=========================================================
REAL-TIME CAMERA → PYTORCH TENSOR → SHARED MEMORY PIPELINE
=========================================================

This program demonstrates:

1. Camera capture (OpenCV)
2. Image → PyTorch tensor conversion
3. Shared memory communication between processes
4. AI-ready tensor pipeline (for YOLO / CLIP / LLMs)

Works on MacBook (Apple Silicon / M5) using AVFoundation.
"""

import cv2
import numpy as np
import torch
import time
from multiprocessing import shared_memory, Process


# =========================================================
# 1. CONFIGURATION (you can change these values)
# =========================================================

WIDTH = 640          # image width
HEIGHT = 480         # image height
CHANNELS = 3         # RGB image has 3 channels

# PyTorch uses CHW format: (Channels, Height, Width)
TENSOR_SHAPE = (CHANNELS, HEIGHT, WIDTH)

# total number of elements in tensor
TENSOR_SIZE = CHANNELS * HEIGHT * WIDTH


# =========================================================
# 2. CAMERA WRITER PROCESS (Producer)
#    - captures camera frames
#    - converts them into PyTorch tensor format
#    - writes into shared memory
# =========================================================

def camera_writer(shm_name):
    """
    This process runs the camera and writes frames into shared memory.
    """

    # Connect to shared memory created in main()
    shm = shared_memory.SharedMemory(name=shm_name)

    # Treat shared memory as a 1D float32 array
    buffer = np.ndarray((TENSOR_SIZE,), dtype=np.float32, buffer=shm.buf)

    # Open Mac camera (important for macOS compatibility)
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("❌ Camera could not be opened")
        return

    print("📸 Camera writer started...")

    while True:

        # Step 1: read frame from camera
        ret, frame = cap.read()
        if not ret:
            continue

        # Step 2: resize so all frames are same shape
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        # Step 3: OpenCV gives BGR → convert to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Step 4: convert to float32 and normalize (0 → 1)
        frame = frame.astype(np.float32) / 255.0

        # Step 5: convert HWC → CHW (PyTorch standard format)
        tensor = np.transpose(frame, (2, 0, 1))

        # Step 6: flatten tensor into 1D array for shared memory
        buffer[:] = tensor.reshape(-1)

        # Step 7: control FPS (1 frame per second)
        time.sleep(1)


# =========================================================
# 3. AI MODEL FUNCTION (Consumer logic)
#    - This is where you plug in YOLO / CLIP / LLaVA
# =========================================================

def run_ai_model(tensor):
    """
    This function simulates AI processing.

    In real use, you could plug in:
    - YOLO (object detection)
    - CLIP (image classification)
    - LLaVA (vision + language model)
    """

    print("🧠 AI received tensor:")
    print("   shape:", tensor.shape)
    print("   dtype:", tensor.dtype)

    # Example: add batch dimension for PyTorch models
    # input_tensor = tensor.unsqueeze(0)

    # Example model inference:
    # output = model(input_tensor)

    return None


# =========================================================
# 4. CAMERA READER PROCESS (Consumer)
#    - reads shared memory
#    - converts back into PyTorch tensor
#    - sends to AI model
# =========================================================

def camera_reader(shm_name):
    """
    This process reads tensor data from shared memory.
    """

    # Connect to shared memory
    shm = shared_memory.SharedMemory(name=shm_name)

    # Interpret memory as float32 array
    buffer = np.ndarray((TENSOR_SIZE,), dtype=np.float32, buffer=shm.buf)

    print("👀 AI reader started...")

    while True:

        # Step 1: reshape flat memory → tensor shape (C, H, W)
        tensor_np = buffer.reshape(TENSOR_SHAPE)

        # Step 2: convert NumPy → PyTorch tensor
        tensor = torch.from_numpy(tensor_np.copy())

        # Step 3: send tensor to AI model
        run_ai_model(tensor)

        # Step 4: wait 1 second before next frame
        time.sleep(1)


# =========================================================
# 5. MAIN PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    # Step 1: create shared memory block
    # multiply by 4 because float32 = 4 bytes per value
    shm = shared_memory.SharedMemory(create=True, size=TENSOR_SIZE * 4)

    try:
        # Step 2: create two parallel processes
        writer_process = Process(target=camera_writer, args=(shm.name,))
        reader_process = Process(target=camera_reader, args=(shm.name,))

        # Step 3: start both processes
        writer_process.start()
        reader_process.start()

        # Step 4: wait for both processes forever
        writer_process.join()
        reader_process.join()

    finally:
        # Step 5: cleanup shared memory
        shm.close()
        shm.unlink()