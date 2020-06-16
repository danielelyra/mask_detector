import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN
from tensorflow.keras.models import load_model

np.set_printoptions(suppress=True)

detector = MTCNN()
model = load_model("./facemask_32_neuronios_30epoca.h5")
cap = cv2.VideoCapture(0)  # abrir a câmera
size = (224, 224)


def predicao(face, frame):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    x1, y1, w, h = face['box']
    x2, y2 = x1 + w, y1 + h

    roi = frame[y1:y2, x1:x2]

    # ajusta o tamanho da imagem
    roi = cv2.resize(roi, size)

    if np.sum([roi]) != 0:
        # normalização da imagem
        roi = (roi.astype(np.float32)/127.0) - 1
        data[0] = roi

        # predição
        pred = model.predict(data)
        pred = pred[0]  # pega o vetor interno da classificação no modelo
        print('predição: ', pred)

        if pred[1] >= pred[0]: 
            label = 'MASK'
            color = (0, 255, 0)
        else:
            label = 'NO MASK'
            color = (0, 0, 255)

        label_position = (x1, y1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    else:
        cv2.putText(frame, 'No Face Found', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

    return label


while True:
    _, frame = cap.read()  # pega o frame e transforma em imagem
    label = 'BACKGROUND'
    faces_list = detector.detect_faces(frame)  # armazena em lista todas as posições das faces capturadas
    people = 0

    print('faces', len(faces_list))
    for face in faces_list:
        try:
            label = predicao(face, frame)
            print(label)
            if label == 'NO MASK':
                people = people + 1
        except Exception as exp:
            print(exp)

    print('--')

    #  labels pra tela de captura
    cv2.rectangle(frame, (0, 0), (200, 100), (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, "NO MASKS : " + str(people), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(frame, "MASKS : " + str(len(faces_list) - people), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    #  exibe e imagem manipulada na tela
    cv2.imshow('MASK DETECTOR', frame)

    #  para encerrar
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
