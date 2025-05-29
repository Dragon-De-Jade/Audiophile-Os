export interface LyrionStatus {
  status: 'playing' | 'paused' | 'stopped' | 'unknown';
  nowPlaying?: {
    artist: string;
    album: string;
    title: string;
  };
  volume: number; // Percentage 0-100
  // Add other status details here as needed
}

const mockStatus: LyrionStatus = {
  status: 'playing',
  nowPlaying: {
    artist: 'Fairuz',
    album: 'Andaloussiyat',
    title: 'Ya Shady Al Alhan',
  },
  volume: 75,
};

export const getLyrionStatus = async (): Promise<LyrionStatus> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate potential changes in status for more dynamic mock
      // For example, randomly change volume or song
      const currentMockStatus = { ...mockStatus, volume: Math.floor(Math.random() * 101) };
      console.info('LyrionApiService: getLyrionStatus called, returning mock status.');
      resolve(currentMockStatus);
    }, 50);
  });
};

export const sendLyrionCommand = async (command: string, params?: any): Promise<any> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.info(`LyrionApiService: sendLyrionCommand called with command: ${command}, params:`, params);
      let responseMessage = `Lyrion command '${command}' processed (mock).`;
      
      // Potentially update mockStatus based on command
      if (command === 'play') {
        mockStatus.status = 'playing';
        responseMessage = 'Lyrion is now playing (mock).';
      } else if (command === 'pause') {
        mockStatus.status = 'paused';
        responseMessage = 'Lyrion is now paused (mock).';
      } else if (command === 'stop') {
        mockStatus.status = 'stopped';
        mockStatus.nowPlaying = undefined; // Clear now playing on stop
        responseMessage = 'Lyrion is now stopped (mock).';
      } else if (command === 'setVolume' && params && typeof params.level === 'number') {
        mockStatus.volume = Math.max(0, Math.min(100, params.level)); // Clamp volume between 0 and 100
        responseMessage = `Lyrion volume set to ${mockStatus.volume} (mock).`;
      } else if (command === 'setVolume') {
        responseMessage = `Lyrion command 'setVolume' requires 'level' parameter (mock).`;
         resolve({
          success: false,
          commandReceived: command,
          paramsReceived: params,
          message: responseMessage,
        });
        return;
      }

      resolve({
        success: true,
        commandReceived: command,
        paramsReceived: params,
        message: responseMessage,
        updatedStatus: mockStatus, // Optionally return the new status
      });
    }, 50);
  });
};
