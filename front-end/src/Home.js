import React from 'react';
import { ChatFeed, Message } from 'react-chat-ui';
import styled from 'styled-components';
import InputGroup from 'react-bootstrap/InputGroup'
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';
import Button from 'react-bootstrap/Button';
import io from 'socket.io-client';

const Style = styled.div`
  .inputBox {
    display: flex;
    flex-direction: row;
  }

  .sendButton {
  }
`;

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.state = {messages: [], nextMessage: ""};
    this.sendHandler = this.sendHandler.bind(this);
    this.changeHandler = this.changeHandler.bind(this);
  }

  componentDidMount() {
    this.endpoint = 'https://heal-bot.herokuapp.com';
    this.socket = io(this.endpoint, {transports: ['websocket'], upgrade: false});
    console.log(this.socket)
    this.socket.on('response', (response) => {
      console.log(response)
      this.receiveMessage(response);
    });
  }

  componentWillUnmount() {
    console.log(this.socket)
    this.socket.emit('disconnect');
    this.socket.off()
  }

  changeHandler(event) {
    console.log(event.target.value)
    this.setState({nextMessage: event.target.value});
  }

  receiveMessage({ message }) {
    var splitMessages = message.split("\n");
    for (let i = 0; i < splitMessages.length; i++) {
      this.setState({messages: this.state.messages.concat(new Message({id: 1, message: splitMessages[i] }))})
    }
  }

  sendHandler(event) {
    event.preventDefault();
    console.log(this.socket)
    console.log('Sending')
    this.socket.emit('sendMessage', {message: this.state.nextMessage});
    let newMessage = new Message({id: 0, message: this.state.nextMessage});
    this.setState({messages: this.state.messages.concat(newMessage), nextMessage: ''});
    var form = document.getElementById("chatbox");
    form.reset();
  }

  render() {
    return (
      <Style>
        <ChatFeed
          messages={this.state.messages}
            bubbleStyles={
              {
              text: {
                  fontSize: 14
              },
              chatbubble: {
                  borderRadius: 30,
                  padding: 20
              }
              }
            }
            showSenderName
        />
        <Form onSubmit={this.sendHandler} id='chatbox'>
          <InputGroup>
            <FormControl
              placeholder="Send a message..."
              onChange={this.changeHandler}
            />
            <InputGroup.Append>
              <Button variant="outline-secondary" type="submit" className="sendButton">Send</Button>
            </InputGroup.Append>
          </InputGroup>
        </Form>
      </Style>
    )
  }
}

export default Home;