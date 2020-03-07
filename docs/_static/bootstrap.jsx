import React, {useState} from 'react';
import ReactDOM from 'react-dom';

import Prism from 'prismjs';
import 'prismjs/components/prism-protobuf';
import 'prismjs/themes/prism.css';

import ClipboardJS from "clipboard";

import {TypeInfo} from './typeinfo';

const VALIDATE_PROTO = 'validate/validate.proto';

const LANGUAGES = [
  {value: 'python', title: 'Python'},
];

const WireType = {
    Input: 1,
    Output: 2,
};

const Reach = {
  Localhost: 'LOCALHOST',
  Namespace: 'NAMESPACE',
  Cluster: 'CLUSTER',
  External: 'EXTERNAL',
};

const Expose = {
  Private: "PRIVATE",
  Headless: "HEADLESS",
  Internal: "INTERNAL",
  Public: "PUBLIC",
};

function useSetter(setter) {
  return (event) => setter(event.target.value)
}

function toggler(setter, value) {
  return () => setter(!value)
}

function itemSetter(value, setValue, i, name) {
  return (itemValue) => {
    setValue([
      ...value.slice(0, i),
      {...value[i], [name]: itemValue},
      ...value.slice(i + 1),
    ]);
  }
}

function itemDeleter(value, setValue, i) {
  return () => {
    setValue([
      ...value.slice(0, i),
      ...value.slice(i + 1),
    ]);
  }
}

function formatField(i, wire, options) {
  return `${wire.config} ${wire.configName} = ${i} [\n        ${options.join(',\n        ')}\n    ];`;
}

function formatInput(i, wire, deployEnabled) {
  let options = [];
  if (!wire.optional) {
    options.push('(validate.rules).message.required = true');
  }
  options.push(`(harness.wire).input.type = "${wire.value}"`);
  if (deployEnabled && wire.reach.length > 0) {
    options.push(`(harness.wire).input.reach = ${wire.reach}`);
  }
  return formatField(i, wire, options);
}

function formatOutput(i, wire, deployEnabled) {
  let options = [];
  if (!wire.optional) {
    options.push('(validate.rules).message.required = true');
  }
  options.push(`(harness.wire).output.type = "${wire.value}"`);
  if (deployEnabled && wire.expose.length > 0) {
    options.push(`(harness.wire).output.expose = ${wire.expose}`);
  }
  return formatField(i, wire, options);
}

function collectImports(inputs, outputs) {
  const items = new Set(['harness/wire.proto']);
  inputs.map(w => {
    items.add(w.configProto);
    if (!w.optional) {
      items.add(VALIDATE_PROTO);
    }
  });
  outputs.map(w => {
    items.add(w.configProto);
    if (!w.optional) {
      items.add(VALIDATE_PROTO);
    }
  });
  return Array.from(items).sort();
}

function renderConfig(serviceName, deployEnabled, repository, inputs, outputs) {
  const imports = collectImports(inputs, outputs);

  let sourceLines = [
    `syntax = "proto3";`,
    '',
    `package ${serviceName};`,
  ];
  sourceLines.push('');
  imports.map(value => sourceLines.push(`import "${value}";`));
  sourceLines.push('');
  sourceLines.push(`message Configuration {`);
  sourceLines.push(`    option (harness.service).name = "${serviceName}";`);
  if (deployEnabled) {
    sourceLines.push(`    option (harness.service).container.repository = "${repository}";`);
  }
  if (inputs.length > 0 || outputs.length > 0) {
    sourceLines.push('');
  }
  let fieldNumber = 1;
  inputs.map(w => {
    sourceLines.push(`    ${formatInput(fieldNumber, w, deployEnabled)}`);
    fieldNumber++;
  });
  outputs.map(w => {
    sourceLines.push(`    ${formatOutput(fieldNumber, w, deployEnabled)}`);
    fieldNumber++;
  });
  sourceLines.push('}');

  return Prism.highlight(
    sourceLines.join('\n'),
    Prism.languages.protobuf,
    'protobuf',
  );
}

function Input(props) {
  const hasReach = props.deployEnabled && TypeInfo.hasOwnProperty(props.wire.config);
  return (
    <div className="bootstrap-value bootstrap-wire">
      <span className="bootstrap-wire-value">{props.wire.value}</span>
      <div className="bootstrap-wire-inputs">
        <input className="bootstrap-wire-name" placeholder="name" type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
        <label>
          <input checked={props.wire.optional} onChange={toggler(props.setOptional, props.wire.optional)} type="checkbox"/>
          Optional
        </label>
        <select value={props.wire.reach} onChange={useSetter(props.setReach)} disabled={!hasReach}>
          <option key={-1} value="">---</option>
          {Object.entries(Reach).map(([key, value]) => {
            return <option key={value} value={value}>{key}</option>
          })}
        </select>
        <button onClick={props.delete}>Delete</button>
      </div>
    </div>
  )
}

function Output(props) {
  const hasExpose = props.deployEnabled && TypeInfo.hasOwnProperty(props.wire.config);
  return (
    <div className="bootstrap-value bootstrap-wire">
      <span className="bootstrap-wire-value">{props.wire.value}</span>
      <div className="bootstrap-wire-inputs">
        <input className="bootstrap-wire-name" placeholder="name" type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
        <label>
          <input checked={props.wire.optional} onChange={toggler(props.setOptional, props.wire.optional)} type="checkbox"/>
          Optional
        </label>
        <select value={props.wire.expose} onChange={useSetter(props.setExpose)} disabled={!hasExpose}>
          <option key={-1} value="">---</option>
          {Object.entries(Expose).map(([key, value]) => {
            return <option key={value} value={value}>{key}</option>
          })}
        </select>
        <button onClick={props.delete}>Delete</button>
      </div>
    </div>
  )
}

function AddWireDialog(props) {
  const [wire, setWire] = useState("");

  function addWire(event) {
    props.addWire(wire);
  }

  return <div className={props.className}>
    <select value={wire} onChange={useSetter(setWire)}>
      <option key={-1} value="">--- select ---</option>
      {props.wires.map((wire, i) => {
        return <option key={i} value={wire.value}>{wire.value}</option>
      })}
    </select>
    <button onClick={addWire} disabled={wire === ""}>Add</button>
  </div>
}

function collectRequirements(inputs, outputs) {
  const items = new Set(['harness']);
  inputs.map(w => {
    w.requirements.map(v => items.add(v));
  });
  outputs.map(w => {
    w.requirements.map(v => items.add(v));
  });
  return Array.from(items).sort();
}

function Bootstrap(props) {
  const wires = props.wiresData.map((w) => {
    return {
      ...w,
      type: (w.type === 'input'? WireType.Input: WireType.Output),
    }
  });

  const [serviceName, setServiceName] = useState('');
  const [runtime, setRuntime] = useState('python');

  const [deployEnabled, setDeployEnabled] = useState(true);
  const [repository, setRepository] = useState('');

  const [inputs, setInputs] = useState([]);
  const [outputs, setOutputs] = useState([]);

  function addInput(wire) {
    const reach = TypeInfo.hasOwnProperty(wire.config)? Reach.Cluster: '';
    setInputs([...inputs, {
      ...wire,
      optional: false,
      configName: '',
      reach: reach,
    }]);
  }

  function addOutput(wire) {
    const expose = TypeInfo.hasOwnProperty(wire.config)? Expose.Internal: '';
    setOutputs([...outputs, {
      ...wire,
      optional: false,
      configName: '',
      expose: expose,
    }]);
  }

  function addWire(name) {
    const wire = wires.find(wire => wire.value === name);
    if (wire.type === WireType.Input) {
      addInput(wire);
    } else if (wire.type === WireType.Output) {
      addOutput(wire);
    } else {
      throw `Unknown wire type: ${wire.type}`
    }
  }

  let configMarkup = {__html: renderConfig(
    serviceName, deployEnabled, repository, inputs, outputs,
  )};

  const requirements = collectRequirements(inputs, outputs);

  return (
    <div className="bootstrap">
      <div className="bootstrap-row">
        <label className="bootstrap-key">Service Name</label>
        <input className="bootstrap-value" type="text" placeholder="bazinga" value={serviceName} onChange={useSetter(setServiceName)}/>
      </div>
      <div className="bootstrap-row">
        <label className="bootstrap-key">Runtime</label>
        <div className="bootstrap-value">
          {LANGUAGES.map(({value, title}) => {
            return (
              <label key={value}>
                <input type="radio" value={value}
                       checked={value === runtime}
                       onChange={useSetter(setRuntime)}/>
                {title}
              </label>
            )
          })}
        </div>
      </div>
      <div className="bootstrap-row">
        <label className="bootstrap-key">Deployment</label>
        <label className="bootstrap-value">
          <input type="checkbox" checked={deployEnabled} onChange={toggler(setDeployEnabled, deployEnabled)}/>
          Enable
        </label>
      </div>
      {deployEnabled && <div className="bootstrap-row">
        <label className="bootstrap-key">Docker Image Repository</label>
        <input className="bootstrap-value" type="text" placeholder="registry.local/group/project" value={repository} onChange={useSetter(setRepository)}/>
      </div>}
      <div className="bootstrap-row">
        <label className="bootstrap-key">Add Wire</label>
        <AddWireDialog className="bootstrap-value" wires={wires} addWire={addWire} />
      </div>
      {inputs.length > 0 && <div className="bootstrap-row">
        <div className="bootstrap-key">&nbsp;</div>
        <div className="bootstrap-value">Inputs:</div>
      </div>}
      <div>
        {inputs.map((w, i) => {
          return <div className="bootstrap-row" key={i}>
            <div className="bootstrap-key">&nbsp;</div>
            <Input wire={w}
                   deployEnabled={deployEnabled}
                   setConfigName={itemSetter(inputs, setInputs, i, 'configName')}
                   setOptional={itemSetter(inputs, setInputs, i, 'optional')}
                   setReach={itemSetter(inputs, setInputs, i, 'reach')}
                   delete={itemDeleter(inputs, setInputs, i)}/>
          </div>
        })}
      </div>
      {outputs.length > 0 && <div className="bootstrap-row">
        <div className="bootstrap-key">&nbsp;</div>
        <div className="bootstrap-value">Outputs:</div>
      </div>}
      <div>
        {outputs.map((w, i) => {
          return <div className="bootstrap-row" key={i}>
            <div className="bootstrap-key">&nbsp;</div>
            <Output wire={w}
                    deployEnabled={deployEnabled}
                    setConfigName={itemSetter(outputs, setOutputs, i, 'configName')}
                    setOptional={itemSetter(outputs, setOutputs, i, 'optional')}
                    setExpose={itemSetter(outputs, setOutputs, i, 'expose')}
                    delete={itemDeleter(outputs, setOutputs, i)}/>
          </div>
        })}
      </div>
      <div>
        <h3>Configuration</h3>
        <div className="cbcopy-container">
          {ClipboardJS.isSupported() && <button className="cbcopy-btn" data-clipboard-target="#config">copy</button>}
          <pre dangerouslySetInnerHTML={configMarkup} id="config"/>
        </div>
      </div>
      <div>
        <h3>Requirements</h3>
        <div className="cbcopy-container">
          {ClipboardJS.isSupported() && <button className="cbcopy-btn" data-clipboard-target="#requirements">copy</button>}
          <pre id="requirements">{requirements.join('\n')}</pre>
        </div>
      </div>
    </div>
  )
}

const mountPoint = document.getElementById('placeholder');
const wiresDataElement = document.getElementById('wires-data');
const wiresData = JSON.parse(wiresDataElement.innerText);

ReactDOM.render(<Bootstrap wiresData={wiresData}/>, mountPoint);

const clipboard = new ClipboardJS('.cbcopy-btn');
clipboard.on('success', (event) => {
    event.clearSelection();
});
