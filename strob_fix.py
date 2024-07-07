import cv2
import numpy as np
import time


def fix_flash(frame, prev_frame):
    """Attempt to reduce flash brightness by averaging with the previous frame."""
    fixed_frame = cv2.addWeighted(frame, 0.5, prev_frame, 0.5, 0)
    return fixed_frame

def apply_black_white(frame):
    """Convert a frame to black and white."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bw_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
    return bw_frame

def get_intensity_difference(frame1, frame2):
    """Calculate the frame-wise intensity difference."""
    if len(frame1.shape) == 3 and frame1.shape[2] == 3:  # Check if frame is BGR
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    else:  # Grayscale frames
        gray1 = frame1
        gray2 = frame2
    return np.abs(np.mean(gray1) - np.mean(gray2))

def detect_strobing_intervals(cap, threshold=15, frame_skip=1):
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second of the video
    ret, prev_frame = cap.read()
    strobing_intervals = []
    currently_strobing = False
    start_frame = None
    frame_index = 0
    
    while ret:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_index % frame_skip == 0:
            mean_diff = get_intensity_difference(prev_frame, frame)
            if mean_diff > threshold:
                if not currently_strobing:
                    currently_strobing = True
                    start_frame = frame_index
            else:
                if currently_strobing:
                    start_time = start_frame / fps
                    end_time = frame_index / fps
                    strobing_intervals.append((start_time, end_time))
                    currently_strobing = False
        prev_frame = frame
        frame_index += 1
    
    if currently_strobing:
        start_time = start_frame / fps
        end_time = frame_index / fps
        strobing_intervals.append((start_time, end_time))
    
    return strobing_intervals

def merge_close_intervals(intervals, gap_threshold=0.7):
    if not intervals:
        return []
    
    merged = [intervals[0]]
    for current_start, current_end in intervals[1:]:
        last_end = merged[-1][1]
        if current_start - last_end <= gap_threshold:
            merged[-1] = (merged[-1][0], current_end)
        else:
            merged.append((current_start, current_end))
    
    return merged

def is_in_strobing_intervals(current_time, intervals):
    for start_time, end_time in intervals:
        if start_time <= current_time <= end_time:
            return True
    return False

def start_stream(inputFile, outputFile,threshold, frame_skip, codecName='mp4v'):
    cap = cv2.VideoCapture(inputFile)
    if not cap.isOpened():
        print("Error opening input video stream")
        return
    
    # Detect strobing intervals before processing frames
    strobing_intervals = detect_strobing_intervals(cap,threshold, frame_skip)

    cap.release()
    # return strobing_intervals
    strobing_intervals = merge_close_intervals(strobing_intervals)
    cap.release()  # Release the cap to reset
    
    cap = cv2.VideoCapture(inputFile)  # Re-open to start processing
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*codecName), fps, (frame_width, frame_height))
    
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        current_time = count / fps
        
        # frame_brightness = get_brightness(frame)
        # Check if current frame is within any of the strobing intervals
        if is_in_strobing_intervals(current_time, strobing_intervals):
            frame = apply_black_white(frame)
            frame = fix_flash(frame, prev_frame)
        # else:
        #     if count > 0 and abs(frame_brightness - prev_brightness) > 30:  # Flash detection threshold
        #         frame = fix_flash(frame, prev_frame)
        
        out.write(frame)
        prev_frame = frame
        # prev_brightness = frame_brightness
        count += 1
    
    out.release()
    cap.release()

# Example usage in a notebook
# a = time.time()
# inputFile = 'videos/test_video.mp4'  # Update this path
# outputFile = 'videos/output_video.mp4'  # Update this path

# start_stream(inputFile, outputFile)
# print(time.time()-a)
