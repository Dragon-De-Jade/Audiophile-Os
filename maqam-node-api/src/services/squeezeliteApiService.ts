export interface SqueezeliteStatus {
  status: 'active' | 'inactive' | 'error';
  playerName: string;
  connectedToServerAddress: string; // e.g., '127.0.0.1:9000'
  // Add other relevant Squeezelite status details here
}

const mockPlayerName = 'MAQAM_Player_Squeeze';
let mockServerAddress = '127.0.0.1:3483'; // Typical Squeezebox server port for CLI
let mockCurrentStatus: SqueezeliteStatus = {
  status: 'active',
  playerName: mockPlayerName,
  connectedToServerAddress: mockServerAddress,
};

export const getSqueezeliteStatus = async (): Promise<SqueezeliteStatus> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.info('SqueezeliteApiService: getSqueezeliteStatus called, returning mock status.');
      resolve({ ...mockCurrentStatus }); // Return a copy
    }, 50); 
  });
};

export const sendSqueezeliteCommand = async (command: string, params?: any): Promise<any> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.info(`SqueezeliteApiService: sendSqueezeliteCommand called with command: ${command}, params:`, params);
      let responseMessage = `Squeezelite command '${command}' processed (mock).`;
      let success = true;

      switch (command.toLowerCase()) {
        case 'connect':
          if (params && params.serverAddress) {
            mockCurrentStatus.status = 'active';
            mockCurrentStatus.connectedToServerAddress = params.serverAddress;
            mockServerAddress = params.serverAddress;
            responseMessage = `Squeezelite connected to ${params.serverAddress} (mock).`;
          } else {
            success = false;
            responseMessage = `Squeezelite command 'connect' requires 'serverAddress' parameter (mock).`;
          }
          break;
        case 'disconnect':
          mockCurrentStatus.status = 'inactive';
          // mockCurrentStatus.connectedToServerAddress = ''; // Or some indicator of not connected
          responseMessage = `Squeezelite disconnected (mock).`;
          break;
        case 'set_name':
          if (params && params.name && typeof params.name === 'string' && params.name.trim() !== '') {
            mockCurrentStatus.playerName = params.name.trim();
            responseMessage = `Squeezelite player name set to '${mockCurrentStatus.playerName}' (mock).`;
          } else {
            success = false;
            responseMessage = `Squeezelite command 'set_name' requires a non-empty 'name' parameter (mock).`;
          }
          break;
        case 'start':
             mockCurrentStatus.status = 'active';
             responseMessage = `Squeezelite process started (mock).`;
             break;
        case 'stop':
            mockCurrentStatus.status = 'inactive';
            // mockCurrentStatus.connectedToServerAddress = ''; // Reset connection on stop
            responseMessage = `Squeezelite process stopped (mock).`;
            break;
        // Add more mock command handlers as needed
        default:
          // For unknown commands, still return success for mock, but indicate it's a generic handler
          responseMessage = `Squeezelite command '${command}' received and processed by generic handler (mock).`;
          break;
      }

      resolve({
        success,
        commandReceived: command,
        paramsReceived: params,
        message: responseMessage,
        updatedStatus: { ...mockCurrentStatus }, // Return a copy of the potentially updated status
      });
    }, 50);
  });
};
