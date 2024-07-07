import cv2
import numpy as np
import time
import sys
import argparse


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

def detect_strobing_intervals(cap, threshold=25, frame_skip=1, gap_threshold=0.7, consecutive_strobe_threshold=5):
    
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second of the video
    print("video_fps", fps)
    ret, prev_frame = cap.read()
    currently_strobing = False
    start_frame = None
    frame_index = 0
    strobe_end_time = 9999
    start_processing_time = time.time()  # Record the start time
    frame_count = 0
    latency_times = []
    consecutive_strobe_count = 0  # Counter for consecutive strobing frames
    while ret:
        ret, frame = cap.read()
        start_time_frame = time.time()
        if not ret:
            break

        if frame_index % frame_skip == 0:
            start_frame = frame_index
            frame_start_time = start_frame / fps
            mean_diff = get_intensity_difference(prev_frame, frame)
            time_elapsed_since_last_strobe = frame_start_time - strobe_end_time

            if mean_diff > threshold:
                if not currently_strobing:
                    currently_strobing = True
                    # strobe_start_time = start_frame / fps
                    consecutive_strobe_count = 1
                else:
                    consecutive_strobe_count += 1
            else:
                if currently_strobing:  # Check if coming out of strobing interval
                    if consecutive_strobe_count >= consecutive_strobe_threshold:
                        strobe_end_time = frame_index / fps
                    currently_strobing = False
                consecutive_strobe_count = 0  # Reset counter if frame is not strobing

            if time_elapsed_since_last_strobe > 0 and time_elapsed_since_last_strobe <= gap_threshold:
                currently_strobing = True
            if currently_strobing:
                frame = apply_black_white(frame)
                frame = fix_flash(frame, prev_frame)

            end_time_frame = time.time()
            frame_latency = end_time_frame - start_time_frame
            latency_times.append(frame_latency)
            target_fps = fps + 4.5  # Assuming target_fps is the same as the input video's fps
            target_frame_interval = 1.0 / target_fps  # Interval between frames
            delay_time = max(1, int((target_frame_interval - frame_latency) * 1000))
            cv2.imshow("output_video", frame)

        frame_count += 1
        prev_frame = frame
        frame_index += 1

        if cv2.waitKey(delay_time) & 0xFF == ord('q'):
            break

    # Calculate FPS
    end_processing_time = time.time()  # Record the end time
    elapsed_time = end_processing_time - start_processing_time
    if elapsed_time == 0:  # Prevent division by zero
        elapsed_time = 1e-6
    fpps = frame_count / elapsed_time
    print("Processing speed (FPS):", fpps)
    average_latency = sum(latency_times) / len(latency_times)
    print("Average processing latency:", average_latency)
    cap.release()
    cv2.destroyAllWindows()
    return True

def start_stream(inputFile,threshold=25, frame_skip=1, gap_threshold=0.7, consecutive_strobe_threshold=5, codecName='mp4v'):
    cap = cv2.VideoCapture(inputFile)
    if not cap.isOpened():
        print("Error opening input video stream")
        return

    detect_strobing_intervals(cap)

# Example usage
if __name__ == '__main__':    

    parser = argparse.ArgumentParser(description='Mitigates strobbing effects in video')
    parser.add_argument('--inputFile', type=str, help='path of the given video file')
    parser.add_argument('--threshold', type=int, default=25, help='threshold for strobbing effect')
    parser.add_argument('--frame_skip', type=int, default=1, help='frames to skip in video')
    parser.add_argument('--gap_threshold', type=int, default=0.7, help='gap between strobbing frames')
    parser.add_argument('--consecutive_strobe_threshold', type=int ,default=5, help='strobbing frame window size')
    args = parser.parse_args()

    start_stream(**vars(args))
