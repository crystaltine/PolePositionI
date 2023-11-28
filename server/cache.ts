export default class ClientData {

    public port: number;

    public keyData: boolean[] = [false, false, false, false]; // forward, backward, left, right

    /**
     * Index 0: Distance along the track
     * Index 1: Velocity along the track
     * Index 2: Acceleration along the track
     * 
     * Index 3: Distance horizontally on track (for sliding left/right)
     * Index 4: Velocity horizontally on track
     * Index 5: Acceleration horizontally on track
     */
    public positionData: number[] = [0, 0, 0, 0, 0, 0]

    constructor(port: number) {
        this.port = port;
    }

    /**
     * Decodes received packet data from client, updates server-side data with decoded.
     * ### Encoding table:
     * 
     * **Bit 1**: 1=keydown, 0=keyup
     * 
     * **Bits 2-3**: 00=forward, 01=backward, 10=left, 11=right
     * 
     * - `000` - forward keyup
     * - `001` - backward keyup
     * - `010` - left keyup
     * - `011` - right keyup
     * - `100` - forward keydown
     * - `101` - backward keydown
     * - `110` - left keydown
     * - `111` - right keydown
     * @param {number} keyBits - int representing a keyevent (though only 3 bits are used) :(
     */
    public updateKeyEvent(keyBits: number) {
        const keyDown = keyBits & 1; // 1 = keydown, 0 = keyup
        const key = keyBits >> 1; // ID of key
        
        this.keyData[key] = Boolean(keyDown);
    }

    /**
     * Updates position data based on current keypresses.
     * 
     * ### Conversion rates:
     * Forward | Backward key pressed: Set `acceleration` to 
     */
    public tick() {
        // TODO
    }
}