"""
Duplicate checker module - Detects if a face already exists in database
"""
import numpy as np
import face_recognition
from modules import FACE_MATCH_THRESHOLD


class DuplicateChecker:
    """Checks for duplicate faces in database"""

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
            scored_people.append((name, score))

        scored_people.sort(key=lambda item: item[1])
        return scored_people
    
    @staticmethod
    def check_duplicate(captured_encodings, known_encodings, known_names, threshold=FACE_MATCH_THRESHOLD):
        """
        Check if captured face already exists in database
        
        Args:
            captured_encodings: List of new encodings captured
            known_encodings: List of all encodings in database
            known_names: List of names corresponding to encodings
            threshold: Distance threshold for matching
        
        Returns:
            (matched_name, min_distance) if duplicate found, else (None, None)
        """
        if len(known_encodings) == 0:
            return None, None
        
        # Calculate average encoding of captured face
        avg_encoding = np.mean(captured_encodings, axis=0)
        
        # Compare against each person using multiple samples
        scored_people = DuplicateChecker._score_people(avg_encoding, known_encodings, known_names)

        if scored_people:
            matched_name, score = scored_people[0]
            if score < threshold:
                return matched_name, score
        
        return None, None