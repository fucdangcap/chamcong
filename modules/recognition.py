"""
Recognition module - Handles face detection and identification
"""
import cv2
import face_recognition
import numpy as np
from modules import FACE_MATCH_THRESHOLD


class RecognitionManager:
    """Manages face recognition and identification"""

    @staticmethod
    def _score_people(encoding, known_encodings, known_names, top_k=3):
        """Score each person by the average of their best distances."""
        distances = face_recognition.face_distance(known_encodings, encoding)
        person_distances = {}

        for index, name in enumerate(known_names):
            person_distances.setdefault(name, []).append(float(distances[index]))

        scored_people = []
        for name, values in person_distances.items():
            best_distances = np.sort(values)[:min(top_k, len(values))]
            score = float(np.mean(best_distances))
            min_distance = float(best_distances[0])
            scored_people.append((name, score, min_distance))

        scored_people.sort(key=lambda item: item[1])
        return scored_people
    
    @staticmethod
    def scan_and_identify(frame, known_encodings, known_names, threshold=FACE_MATCH_THRESHOLD):
        """
        Scan frame and identify faces
        
        Args:
            frame: Input frame from camera
            known_encodings: List of known face encodings
            known_names: List of corresponding names
            threshold: Distance threshold for matching
        
        Returns:
            List of tuples: (name, display_name, box, confidence)
        """
        # Resize and convert frame
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = face_recognition.face_locations(imgS)
        encodings = face_recognition.face_encodings(imgS, faces)
        
        results = []
        for encoding, face_loc in zip(encodings, faces):
            top, right, bottom, left = face_loc
            top, right, bottom, left = top*4, right*4, bottom*4, left*4
            
            name = "Unknown"
            display_name = "Unknown"
            confidence = 0.0
            
            if len(known_encodings) > 0:
                # Compare against each person using multiple samples
                scored_people = RecognitionManager._score_people(
                    encoding, known_encodings, known_names
                )

                if scored_people:
                    best_name, best_score, best_min_distance = scored_people[0]

                    if best_score < threshold:
                        name = best_name.upper()
                        confidence = 1.0 - best_score

                        # Format display name
                        clean_name = name.replace("_", " ")
                        words = clean_name.split()
                        if len(words) >= 2:
                            display_name = words[-2] + " " + words[-1]
                        else:
                            display_name = clean_name
                        display_name = display_name[:16]
                    else:
                        confidence = 1.0 - best_min_distance
            
            results.append((name, display_name, (top, right, bottom, left), confidence))
        
        return results
    
    @staticmethod
    def draw_results_on_frame(frame, results):
        """
        Draw recognition results on frame
        
        Args:
            frame: Input frame
            results: List of recognition results
        
        Returns:
            Frame with drawn results
        """
        for name, display_name, box, confidence in results:
            top, right, bottom, left = box
            
            if name != "Unknown":
                # Matched face - green box
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                text = f"{display_name} ({confidence:.0%})"
                cv2.putText(frame, text, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
            else:
                # Unknown face - red box
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, "UNKNOWN", (left + 6, bottom - 6),
                           cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame